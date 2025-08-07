#
# Copyright (c) Starburst Data, Inc. All rights reserved.
#

from typing import Annotated, Dict, List, Literal, Optional

from pydantic.v1 import Field

from pystarburst._internal.analyzer.expression import Expression, ExpressionUnion
from pystarburst._internal.analyzer.expression.sort import SortOrder


class TableFunctionPartitionSpecDefinition(Expression):
    type: Literal["TableFunctionPartitionSpecDefinition"] = Field("TableFunctionPartitionSpecDefinition", alias="@type")
    over: bool = Field(False)
    partition_spec: Optional[List[Annotated[ExpressionUnion, Field(alias="partitionSpec", discriminator="type")]]]
    order_spec: Optional[List[SortOrder]] = Field(alias="orderSpec")


class TableFunctionExpression(Expression):
    func_name: str = Field(alias="functionName")
    partition_spec: TableFunctionPartitionSpecDefinition = Field(alias="partitionSpec")


class PosArgumentsTableFunction(TableFunctionExpression):
    type: Literal["PosArgumentsTableFunction"] = Field("PosArgumentsTableFunction", alias="@type")
    args: List[Annotated[ExpressionUnion, Field(discriminator="type")]] = Field(alias="arguments")


class NamedArgumentsTableFunction(TableFunctionExpression):
    type: Literal["NamedArgumentsTableFunction"] = Field("NamedArgumentsTableFunction", alias="@type")
    args: Dict[str, Annotated[ExpressionUnion, Field(discriminator="type")]] = Field(alias="arguments")
