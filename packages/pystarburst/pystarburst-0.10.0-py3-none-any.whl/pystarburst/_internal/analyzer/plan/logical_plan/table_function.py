#
# Copyright (c) Starburst Data, Inc. All rights reserved.
#

from typing import Literal, Union

from pydantic.v1 import Field

from pystarburst._internal.analyzer.expression.table_function import (
    NamedArgumentsTableFunction,
    PosArgumentsTableFunction,
)
from pystarburst._internal.analyzer.plan.logical_plan import LogicalPlan


class TableFunctionRelation(LogicalPlan):
    type: Literal["TableFunctionRelation"] = Field("TableFunctionRelation", alias="@type")
    table_function: Union[PosArgumentsTableFunction, NamedArgumentsTableFunction] = Field(alias="tableFunction")
