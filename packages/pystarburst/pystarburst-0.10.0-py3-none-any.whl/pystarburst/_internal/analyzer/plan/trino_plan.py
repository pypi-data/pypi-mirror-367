#
# Copyright (c) Starburst Data, Inc. All rights reserved.
#

import sys
from typing import Dict, List, Optional

import trino
from pydantic.v1 import Field

from pystarburst._internal.analyzer.base_model import BaseModel
from pystarburst._internal.analyzer.plan.logical_plan import LogicalPlanUnion
from pystarburst._internal.error_message import PyStarburstClientExceptionMessages


class TrinoPlan(BaseModel):
    queries: List[str]
    post_actions: Optional[List[str]] = Field(alias="postActions")
    source_plan: Optional[LogicalPlanUnion] = Field(alias="sourcePlan", discriminator="type", exclude=True)
    output: Optional[List["Attribute"]]
    alias_map: Dict[str, str] = Field(alias="aliasMap")
    starburst_dataframe_version: Optional[str] = Field(alias="starburstDataFrameVersion")

    class Decorator:
        @staticmethod
        def wrap_exception(func):
            def wrap(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except trino.exceptions.TrinoUserError as e:
                    tb = sys.exc_info()[2]
                    ne = PyStarburstClientExceptionMessages.SQL_EXCEPTION_FROM_PROGRAMMING_ERROR(e)
                    raise ne.with_traceback(tb) from None

            return wrap

    @property
    def attributes(self) -> List["Attribute"]:
        return self.output

    class Config:
        validate_assignment = True
        frozen = False
