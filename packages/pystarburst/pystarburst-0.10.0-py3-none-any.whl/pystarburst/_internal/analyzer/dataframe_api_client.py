#
# Copyright (c) Starburst Data, Inc. All rights reserved.
#
import base64
import copy
import json
from json import JSONDecodeError
from typing import Union

import zstandard as zstd
from pydantic.v1 import Field
from trino.client import PROXIES, TrinoRequest, logger
from trino.exceptions import TrinoQueryError

from pystarburst._internal.analyzer.base_model import BaseModel
from pystarburst._internal.analyzer.plan.logical_plan import LogicalPlan
from pystarburst._internal.analyzer.plan.trino_plan import TrinoPlan
from pystarburst._internal.utils import PythonObjJSONEncoder
from pystarburst.exceptions import (
    PyStarburstColumnException,
    PyStarburstGeneralException,
    PyStarburstPlanException,
    PyStarburstSQLException,
)


class ErrorResponse(BaseModel):
    message: str
    error_code: str = Field(alias="errorCode")


class Response(BaseModel):
    __root__: Union[TrinoPlan, ErrorResponse] = Field()


class DataFrameApiRequest(TrinoRequest):
    @property
    def statement_url(self) -> str:
        return self.get_url("/v1/dataframe/plan")

    def execute(self, payload):
        # Deep copy of the http_headers dict since they may be modified for this
        # request by the provided additional_http_headers
        http_headers = copy.deepcopy(self.http_headers)
        http_headers.update({"Content-Type": "application/json"})

        http_response = self._post(
            self.statement_url,
            data=json.dumps(payload, cls=PythonObjJSONEncoder),
            headers=http_headers,
            timeout=self._request_timeout,
            proxies=PROXIES,
        )
        return http_response


class DataFrameTableFunction:
    PREFIX = "$zstd:"

    def __init__(self, cursor, session):
        self.cursor = cursor
        self.session = session

    def execute(self, payload):
        payload_json = json.dumps(payload, cls=PythonObjJSONEncoder)
        if (
            not self.session._use_endpoint
            and self.session._starburst_dataframe_version is not None
            and len(payload_json) > 2 * 1024
        ):
            compressed = zstd.compress(payload_json.encode("utf-8"))
            payload_json = DataFrameTableFunction.PREFIX + base64.b64encode(compressed).decode("utf-8")
        try:
            self.cursor.execute(f"SELECT trino_plan FROM TABLE(analyze_logical_plan(?))", [payload_json])
        except TrinoQueryError as e:
            raise PyStarburstSQLException(f"Failed to analyze logical plan: {str(e.message)}") from e
        rows = self.cursor.fetchall()
        return rows[0][0]


class DataframeApiClient:
    def __init__(self, session):
        self.session = session

    def analyze(self, logical_plan: LogicalPlan) -> TrinoPlan:
        conn = self.session._conn._conn
        cursor = self.session._conn._cursor
        if self.session._use_endpoint:
            trino_request = DataFrameApiRequest(
                conn.host,
                conn.port,
                conn._client_session,
                conn._http_session,
                conn.http_scheme,
                conn.auth,
                conn.max_attempts,
                conn.request_timeout,
            )
        else:
            trino_request = DataFrameTableFunction(cursor, self.session)
        payload = self.serialize(logical_plan)
        if self.session._use_endpoint:
            try:
                response = trino_request.execute(payload).json()
            except JSONDecodeError:
                response = trino_request.execute(payload).text
                if "ParsingException" or "TrinoException" in response:
                    raise PyStarburstSQLException(response)
                raise PyStarburstGeneralException(response)
        else:
            response = json.loads(trino_request.execute(payload))
        trino_plan = self.deserialize(response)
        # Keep the original source plan for supporting cloning dataframes
        trino_plan.source_plan = logical_plan
        return trino_plan

    def serialize(self, logical_plan):
        return logical_plan.dict(by_alias=True, exclude_none=True)

    def deserialize(self, json) -> TrinoPlan:
        response = Response.parse_obj(json).__root__

        if isinstance(response, ErrorResponse):
            message = response.message
            error_code = response.error_code
            if error_code == "ANALYSIS_ERROR":
                raise PyStarburstSQLException(message)
            if error_code == "SQL_ERROR":
                raise PyStarburstSQLException(message)
            raise PyStarburstGeneralException(message)

        assert isinstance(response, TrinoPlan)
        return response
