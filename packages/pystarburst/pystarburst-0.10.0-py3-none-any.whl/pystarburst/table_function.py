#
# Copyright (c) 2012-2022 Snowflake Computing Inc. All rights reserved.
# Copyright (c) Starburst Data, Inc. All rights reserved.
#

"""Contains table function related classes."""
from typing import Dict, Iterable, List, Optional, Tuple, Union

from pystarburst._internal.analyzer.analyzer_utils import quote_name
from pystarburst._internal.analyzer.expression.sort import SortDirection, SortOrder
from pystarburst._internal.analyzer.expression.table_function import (
    NamedArgumentsTableFunction,
    PosArgumentsTableFunction,
    TableFunctionExpression,
    TableFunctionPartitionSpecDefinition,
)
from pystarburst._internal.type_utils import ColumnOrName
from pystarburst._internal.utils import validate_object_name
from pystarburst.column import Column, _to_col_if_str

from ._internal.analyzer.plan.trino_plan import TrinoPlan


class TableFunctionCall:
    """Represents a table function call.
    A table function call has the function names, positional arguments, named arguments and the partitioning information.

    The constructor of this class is not supposed to be called directly.
    Instead, use :func:`~pystarburst.function.call_table_function`, which will create an instance of this class.
    Or use :func:`~pystarburst.function.table_function` to create a ``Callable`` object and call it to create an
    instance of this class.
    """

    def __init__(
        self,
        func_name: Union[str, Iterable[str]],
        *func_arguments: ColumnOrName,
        **func_named_arguments: ColumnOrName,
    ) -> None:
        if func_arguments and func_named_arguments:
            raise ValueError("A table function shouldn't have both args and named args")
        self.name: str = func_name  #: The table function name
        self.arguments: Iterable[ColumnOrName] = func_arguments  #: The positional arguments used to call this table function.
        self.named_arguments: Dict[str, ColumnOrName] = (
            func_named_arguments  #: The named arguments used to call this table function.
        )
        self._over = False
        self._partition_by = None
        self._order_by = None
        self._aliases: Optional[Iterable[str]] = None
        self._api_call_source = None

    def _set_api_call_source(self, api_call_source):
        self._api_call_source = api_call_source

    def over(
        self,
        *,
        partition_by: Optional[Union[ColumnOrName, Iterable[ColumnOrName]]] = None,
        order_by: Optional[Union[ColumnOrName, Iterable[ColumnOrName]]] = None,
    ) -> "TableFunctionCall":
        """Specify the partitioning plan for this table function call when you lateral join this table function.

        When a query does a lateral join on a table function, the query feeds data to the table function row by row.
        Before rows are passed to table functions, the rows can be grouped into partitions. Partitioning has two main benefits:

        - Partitioning allows Trino to divide up the workload to improve parallelization and thus performance.
        - Partitioning allows Trino to process all rows with a common characteristic as a group. You can return results that are based on all rows in the group, not just on individual rows.

        Refer to `table functions and partitions <https://trino.io/docs/current/functions/table.html>`__ for more information.

        Args:
            partition_by: Specify the partitioning column(s). It tells the table function to partition by these columns.
            order_by: Specify the ``order by`` column(s). It tells the table function to process input rows with this order within a partition.

        Note that if this function is called but both ``partition_by`` and ``order_by`` are ``None``, the table function call will put all input rows into a single partition.
        If this function isn't called at all, the Trino cluster will use implicit partitioning.
        """
        new_table_function = TableFunctionCall(self.name, *self.arguments, **self.named_arguments)
        new_table_function._over = True

        if isinstance(partition_by, (str, Column)):
            partition_by_tuple = (partition_by,)
        elif partition_by is not None:
            partition_by_tuple = tuple(partition_by)
        else:
            partition_by_tuple = None
        partition_spec = (
            [e._expression if isinstance(e, Column) else Column(e)._expression for e in partition_by_tuple]
            if partition_by_tuple
            else None
        )
        new_table_function._partition_by = partition_spec

        if isinstance(order_by, (str, Column)):
            order_by_tuple = (order_by,)
        elif order_by is not None:
            order_by_tuple = tuple(order_by)
        else:
            order_by_tuple = None
        if order_by_tuple:
            order_spec = []
            if len(order_by_tuple) > 0:
                for e in order_by_tuple:
                    order_spec.append(_create_order_by_expression(e))
            new_table_function._order_by = order_spec
        return new_table_function

    def alias(self, *aliases: str) -> "TableFunctionCall":
        """Alias the output columns from the output of this table function call.

        Args:
            aliases: An iterable of unique column names that do not collide with column names after join with the main table.

        Raises:
            ValueError: Raises error when the aliases are not unique after being canonicalized.
        """
        canon_aliases = [quote_name(col) for col in aliases]
        if len(set(canon_aliases)) != len(aliases):
            raise ValueError("All output column names after aliasing must be unique.")

        self._aliases = canon_aliases
        return self

    as_ = alias


def _create_order_by_expression(e: Union[str, Column]) -> SortOrder:
    if isinstance(e, str):
        return SortOrder(child=Column(e)._expression, direction=SortDirection.ASCENDING)
    elif isinstance(e, Column):
        if isinstance(e._expression, SortOrder):
            return e._expression
        else:  # isinstance(e._expression, Expression):
            return SortOrder(child=e._expression, direction=SortDirection.ASCENDING)
    else:
        raise TypeError("Order By columns must be of column names in str, or a Column object.")


def _create_table_function_expression(
    func: Union[str, List[str], TableFunctionCall],
    *args: ColumnOrName,
    **named_args: ColumnOrName,
) -> TableFunctionExpression:
    over = None
    partition_by = None
    order_by = None
    if args and named_args:
        raise ValueError("A table function shouldn't have both args and named args.")
    if isinstance(func, str):
        fqdn = func
    elif isinstance(func, list):
        for n in func:
            validate_object_name(n)
        fqdn = ".".join(func)
    elif isinstance(func, TableFunctionCall):
        if args or named_args:
            raise ValueError("'args' and 'named_args' shouldn't be used if a TableFunction instance is used.")
        fqdn = func.name
        args = func.arguments
        named_args = func.named_arguments
        over = func._over
        partition_by = func._partition_by
        order_by = func._order_by
    else:
        raise TypeError(
            "'func' should be a function name in str, a list of strs that have all or a part of the fully qualified name, or a TableFunctionCall instance."
        )
    spec = TableFunctionPartitionSpecDefinition(over=over if over else False, partition_spec=partition_by, orderSpec=order_by)
    if args:
        table_function_expression = PosArgumentsTableFunction(
            func_name=fqdn,
            partition_spec=spec,
            args=[_to_col_if_str(arg, "table function")._expression for arg in args],
        )
    else:
        table_function_expression = NamedArgumentsTableFunction(
            func_name=fqdn,
            partition_spec=spec,
            args={arg_name: _to_col_if_str(arg, "table function")._expression for arg_name, arg in named_args.items()},
        )
    return table_function_expression
