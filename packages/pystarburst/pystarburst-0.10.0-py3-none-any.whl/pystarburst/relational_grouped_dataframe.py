#
# Copyright (c) 2012-2022 Snowflake Computing Inc. All rights reserved.
# Copyright (c) Starburst Data, Inc. All rights reserved.
#

import re
from typing import Callable, Dict, List, Tuple, Union

from pystarburst import functions
from pystarburst._internal.analyzer.expression.general import (
    Expression,
    Literal,
    NamedExpression,
)
from pystarburst._internal.analyzer.expression.grouping_set import (
    Cube,
    GroupingSetsExpression,
    Rollup,
)
from pystarburst._internal.analyzer.expression.unary import Alias, UnresolvedAlias
from pystarburst._internal.analyzer.plan.logical_plan.unary import Aggregate, Pivot
from pystarburst._internal.type_utils import ColumnOrName
from pystarburst._internal.utils import parse_positional_args_to_list
from pystarburst.column import Column
from pystarburst.dataframe import DataFrame

INVALID_TRINO_IDENTIFIER_CHARS = re.compile("[^\\x20-\\x7E]")


def _strip_invalid_trino_identifier_chars(identifier: str) -> str:
    return INVALID_TRINO_IDENTIFIER_CHARS.sub("", identifier.replace('"', ""))


def _alias(expr: Expression) -> NamedExpression:
    if isinstance(expr, NamedExpression):
        return expr
    return UnresolvedAlias(child=expr)


def _expr_to_func(expr: str, input_expr: Expression) -> Expression:
    lowered = expr.lower()
    if lowered in ["avg", "average", "mean"]:
        return functions.avg(Column(input_expr))._expression
    elif lowered in ["stddev", "std"]:
        return functions.stddev(Column(input_expr))._expression
    elif lowered in ["count", "size"]:
        return functions.count(Column(input_expr))._expression
    else:
        return functions.function(lowered)(input_expr)._expression


def _str_to_expr(expr: str) -> Callable:
    return lambda input_expr: _expr_to_func(expr, input_expr)


class _GroupType:
    def to_string(self) -> str:
        return self.__class__.__name__[1:-4]


class _GroupByType(_GroupType):
    pass


class _CubeType(_GroupType):
    pass


class _RollupType(_GroupType):
    pass


class _PivotType(_GroupType):
    def __init__(self, pivot_col: Expression, values: List[Expression]) -> None:
        self.pivot_col = pivot_col
        self.values = values


class GroupingSets:
    """Creates a :class:`GroupingSets` object from a list of column/expression sets that you pass
    to :meth:`DataFrame.group_by_grouping_sets`. See :meth:`DataFrame.group_by_grouping_sets` for
    examples of how to use this class with a :class:`DataFrame`. See
    `GROUP BY GROUPING SETS <https://trino.io/docs/current/sql/select.html#complex-grouping-operations>`_
    for its counterpart in SQL (several examples are shown below).

    =============================================================  ==================================
    Python interface                                               SQL interface
    =============================================================  ==================================
    ``GroupingSets([col("a")], [col("b")])``                       ``GROUPING SETS ((a), (b))``
    ``GroupingSets([col("a") , col("b")], [col("c"), col("d")])``  ``GROUPING SETS ((a, b), (c, d))``
    ``GroupingSets([col("a"), col("b")])``                         ``GROUPING SETS ((a, b))``
    ``GroupingSets(col("a"), col("b"))``                           ``GROUPING SETS ((a, b))``
    =============================================================  ==================================
    """

    def __init__(self, *sets: Union[Column, List[Column]]) -> None:
        prepared_sets = parse_positional_args_to_list(*sets)
        prepared_sets = prepared_sets if isinstance(prepared_sets[0], list) else [prepared_sets]
        self._to_expression = GroupingSetsExpression(args=[[c._expression for c in s] for s in prepared_sets])


class RelationalGroupedDataFrame:
    """Represents an underlying DataFrame with rows that are grouped by common values.
    Can be used to define aggregations on these grouped DataFrames.
    """

    def __init__(self, df: DataFrame, grouping_exprs: List[Expression], group_type: _GroupType) -> None:
        self._df = df
        self._grouping_exprs = grouping_exprs
        self._group_type = group_type
        self._df_api_call = None

    def _to_df(self, agg_exprs: List[Expression]) -> DataFrame:
        aliased_agg = []
        for grouping_expr in self._grouping_exprs:
            if isinstance(grouping_expr, GroupingSetsExpression):
                # avoid doing list(set(grouping_expr.args)) because it will change the order
                gr_used = set()
                gr_uniq = [a for arg in grouping_expr.args for a in arg if a not in gr_used and (gr_used.add(a) or True)]
                aliased_agg.extend(gr_uniq)
            else:
                aliased_agg.append(grouping_expr)

        aliased_agg.extend(agg_exprs)

        if isinstance(self._group_type, _GroupByType):
            group_plan = Aggregate(
                grouping_expressions=self._grouping_exprs if len(self._grouping_exprs) else [],
                aggregate_expressions=aliased_agg,
                child=self._df._plan,
            )
        elif isinstance(self._group_type, _RollupType):
            group_plan = Aggregate(
                grouping_expressions=[Rollup(group_by_exprs=self._grouping_exprs)] if len(self._grouping_exprs) else [],
                aggregate_expressions=aliased_agg,
                child=self._df._plan,
            )
        elif isinstance(self._group_type, _CubeType):
            group_plan = Aggregate(
                grouping_expressions=[Cube(group_by_exprs=self._grouping_exprs)] if len(self._grouping_exprs) else [],
                aggregate_expressions=aliased_agg,
                child=self._df._plan,
            )
        elif isinstance(self._group_type, _PivotType):
            group_plan = Pivot(
                pivot_column=self._group_type.pivot_col,
                pivot_values=self._group_type.values,
                aggregates=agg_exprs,
                child=self._df._plan,
            )
        else:  # pragma: no cover
            raise TypeError(f"Wrong group by type {self._group_type}")

        return self._df._with_plan(group_plan)

    def agg(self, *exprs: Union[Column, Tuple[ColumnOrName, str], Dict[str, str]]) -> DataFrame:
        """Returns a :class:`DataFrame` with computed aggregates. See examples in :meth:`DataFrame.group_by`.

        Args:
            exprs: A variable length arguments list where every element is

                - a Column object
                - a tuple where the first element is a column object or a column name and the second element is the name of the aggregate function
                - a list of the above
                - a ``dict`` maps column names to aggregate function names.

        Note:
            The name of the aggregate function to compute must be a valid Trino `aggregate function
            <https://trino.io/docs/current/functions/aggregate.html>`_.

        See also:
            - :meth:`DataFrame.agg`
            - :meth:`DataFrame.group_by`
        """

        def is_valid_tuple_for_agg(e: Union[list, tuple]) -> bool:
            return len(e) == 2 and isinstance(e[0], (Column, str)) and isinstance(e[1], str)

        exprs = parse_positional_args_to_list(*exprs)
        # special case for single list or tuple
        if is_valid_tuple_for_agg(exprs):
            exprs = [exprs]

        agg_exprs = []
        if len(exprs) > 0 and isinstance(exprs[0], dict):
            for k, v in exprs[0].items():
                if not (isinstance(k, str) and isinstance(v, str)):
                    raise TypeError(
                        "Dictionary passed to DataFrame.agg() or RelationalGroupedDataFrame.agg() "
                        f"should contain only strings: got key-value pair with types {type(k), type(v)}"
                    )
                agg_exprs.append(_str_to_expr(v)(Column(k)._expression))
        else:
            for e in exprs:
                if isinstance(e, Column):
                    agg_exprs.append(e._expression)
                elif isinstance(e, (list, tuple)) and is_valid_tuple_for_agg(e):
                    col_expr = e[0]._expression if isinstance(e[0], Column) else Column(e[0])._expression
                    agg_exprs.append(_str_to_expr(e[1])(col_expr))
                else:
                    raise TypeError(
                        "List passed to DataFrame.agg() or RelationalGroupedDataFrame.agg() should "
                        "contain only Column objects, or pairs of Column object (or column name) and strings."
                    )

        return self._to_df(agg_exprs)

    def avg(self, *cols: ColumnOrName) -> DataFrame:
        """Return the average for the specified numeric columns."""
        return self._non_empty_argument_function("avg", *cols)

    mean = avg

    def sum(self, *cols: ColumnOrName) -> DataFrame:
        """Return the sum for the specified numeric columns."""
        return self._non_empty_argument_function("sum", *cols)

    # median not supported in Trino
    # def median(self, *cols: ColumnOrName) -> DataFrame:
    #     """Return the median for the specified numeric columns."""
    #     return self._non_empty_argument_function("median", *cols)

    def min(self, *cols: ColumnOrName) -> DataFrame:
        """Return the min for the specified numeric columns."""
        return self._non_empty_argument_function("min", *cols)

    def max(self, *cols: ColumnOrName) -> DataFrame:
        """Return the max for the specified numeric columns."""
        return self._non_empty_argument_function("max", *cols)

    def count(self) -> DataFrame:
        """Return the number of rows for each group."""
        return self._to_df(
            [
                Alias(
                    child=functions.builtin("count")(Literal(value=1))._expression,
                    name="count",
                )
            ]
        )

    def function(self, agg_name: str) -> Callable:
        """Computes the builtin aggregate ``agg_name`` over the specified columns. Use
        this function to invoke any aggregates not explicitly listed in this class.
        See examples in :meth:`DataFrame.group_by`.
        """
        return lambda *cols: self._function(agg_name, *cols)

    builtin = function

    def _function(self, agg_name: str, *cols: ColumnOrName) -> DataFrame:
        agg_exprs = []
        for c in cols:
            c_expr = Column(c)._expression if isinstance(c, str) else c._expression
            expr = functions.builtin(agg_name)(c_expr)._expression
            agg_exprs.append(expr)
        return self._to_df(agg_exprs)

    def _non_empty_argument_function(self, func_name: str, *cols: ColumnOrName) -> DataFrame:
        if not cols:
            raise ValueError(f"You must pass a list of one or more Columns to function: {func_name}")
        else:
            return self.builtin(func_name)(*cols)
