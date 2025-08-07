#
# Copyright (c) 2012-2022 Snowflake Computing Inc. All rights reserved.
# Copyright (c) Starburst Data, Inc. All rights reserved.
#

from typing import Dict, Iterable, Optional, Union

import pystarburst  # for forward references of type hints
from pystarburst import Literal
from pystarburst._internal.analyzer.analyzer_utils import convert_value_to_sql_option
from pystarburst._internal.analyzer.plan.logical_plan.table import CreateTable, SaveMode
from pystarburst._internal.utils import str_to_enum, validate_object_name


class DataFrameWriter:
    """Provides methods for writing data from a :class:`DataFrame` to supported output destinations.

    To use this object:

    1. Create an instance of a :class:`DataFrameWriter` by accessing the :attr:`DataFrame.write` property.
    2. (Optional) Specify the save mode by calling :meth:`mode`, which returns the same
       :class:`DataFrameWriter` that is configured to save data using the specified mode.
       The default mode is "errorifexists".
    3. Call :meth:`save_as_table` or :meth:`copy_into_location` to save the data to the
       specified destination.
    """

    def __init__(self, dataframe: "pystarburst.dataframe.DataFrame") -> None:
        self._dataframe = dataframe
        self._save_mode = SaveMode.ERRORIFEXISTS

    def mode(self, save_mode: str) -> "DataFrameWriter":
        """Set the save mode of this :class:`DataFrameWriter`.

        Args:
            save_mode: one of the following strings:

                - "append": Append data of this DataFrame to existing data.
                - "overwrite": Overwrite existing data.
                - "errorifexists": Throw an exception if data already exists.
                - "ignore": Ignore this operation if data already exists.

                Default value is "errorifexists".

        Returns:
            The :class:`DataFrameWriter` itself.
        """
        self._save_mode = str_to_enum(save_mode, SaveMode, "`save_mode`")
        return self

    def save_as_table(
        self,
        table_name: Union[str, Iterable[str]],
        *,
        mode: Optional[str] = None,
        column_order: str = "index",
        table_properties: Dict[str, Union[str, bool, int, float]] = None,
        statement_properties: Optional[Dict[str, str]] = None,
    ) -> None:
        """Writes the data to the specified table in a Trino cluster.

        :meth:`saveAsTable` is an alias of :meth:`save_as_table`.

        Args:
            table_name: A string or list of strings that specify the table name or fully-qualified object identifier
                (database name, schema name, and table name).
            mode: One of the following values. When it's ``None`` or not provided,
                the save mode set by :meth:`mode` is used.

                - "append": Append data of this DataFrame to existing data.
                - "overwrite": Overwrite existing data.
                - "errorifexists": Throw an exception if data already exists.
                - "ignore": Ignore this operation if data already exists.

            column_order: When ``mode`` is "append", data will be inserted into the target table by matching column sequence or column name. Default is "index". When ``mode`` is not "append", the ``column_order`` makes no difference.

                - "index": Data will be inserted into the target table by column sequence.
                - "name": Data will be inserted into the target table by matching column names. If the target table has more columns than the source DataFrame, use this one.

            table_properties: Any custom table properties used to create the table.

        Examples:

            >>> df = session.create_dataframe([[1,2],[3,4]], schema=["a", "b"])
            >>> df.write.mode("overwrite").save_as_table("my_table")
            >>> session.table("my_table").collect()
            [Row(A=1, B=2), Row(A=3, B=4)]
            >>> df.write.save_as_table("my_table", mode="append")
            >>> session.table("my_table").collect()
            [Row(A=1, B=2), Row(A=3, B=4), Row(A=1, B=2), Row(A=3, B=4)]
            >>> df.write.mode("overwrite").save_as_table("my_table", table_properties={"format": "parquet"})
            >>> session.table("my_table").collect()
            [Row(A=1, B=2), Row(A=3, B=4)]
            >>> df.write.mode("overwrite").save_as_table("my_table", table_properties={"partitioning": ["a"]})
            >>> session.table("my_table").collect()
            [Row(A=1, B=2), Row(A=3, B=4)]
        """
        save_mode = str_to_enum(mode, SaveMode, "'mode'") if mode else self._save_mode
        full_table_name = table_name if isinstance(table_name, str) else ".".join(table_name)
        validate_object_name(full_table_name)
        if column_order is None or column_order.lower() not in ("name", "index"):
            raise ValueError("'column_order' must be either 'name' or 'index'")
        column_names = self._dataframe.columns if column_order.lower() == "name" else None

        create_table_logic_plan = CreateTable(
            table_name=full_table_name,
            column_names=column_names,
            mode=save_mode,
            query=self._dataframe._plan,
            table_properties=(
                {k: Literal(value=v) for k, v in table_properties.items()} if table_properties is not None else None
            ),
        )
        session = self._dataframe._session
        trino_plan = self._dataframe._session._analyzer.resolve(create_table_logic_plan)
        session._conn.execute(trino_plan, statement_properties=statement_properties)

    saveAsTable = save_as_table

    def copy_into_location(
        self,
        location: str,
        format: str,
        *,
        catalog: Optional[str] = None,
        # partition_by: Optional[Iterable[str]] = None,
        compression: Optional[str] = None,
        separator: Optional[str] = None,
        header: Optional[bool] = None,
    ) -> None:
        """
        Executes UNLOAD command to copy the data to the specified location.

        :param location: An object storage location where the output is written
        :param format: Supported format parameters: ORC, PARQUET, AVRO, RCBINARY, RCTEXT, SEQUENCEFILE, JSON, OPENX_JSON, TEXTFILE, CSV
        :param catalog: A hive catalog where UNLOAD function is registered. If no catalog is provided, session's catalog will be used.
        :param compression: Supported compression parameters: NONE (default), SNAPPY, LZ4, ZSTD, GZIP
        :param separator: Custom separator for the output file. Default is ',' for CSV and '\x01' for TEXTFILE
        :param header: If output file should include header (True) or not (False). Default is False

        The separator and header parameters are applicable only when the format argument is set to CSV or TEXTFILE.

        Each format has its own set of constraints.
        The CSV format exclusively supports VARCHAR columns, and AVRO files do not permit special characters in the column names.

        Examples:
            >>> df = session.create_dataframe([[1,2],[3,4]], schema=["a", "b"])
            >>> df.write.copy_into_location(location="s3://mybucket/my/location", format="CSV")

            >>> df = session.create_dataframe([[1,2],[3,4]], schema=["a", "b"])
            >>> df.write.copy_into_location(location="s3://mybucket/my/location2", format="CSV", catalog="hive", compression="GZIP")
        """
        assert len(self._dataframe._plan.queries) is 1, "Dataframe is expected to have exactly one query plan"
        sub_query = self._dataframe._plan.queries[0].strip()

        hive_catalog = self._dataframe._session.get_current_catalog() if catalog is None else catalog

        partition_clause = ""
        # TODO Once UNLOAD partition is fixed - we can enable it (https://github.com/starburstdata/pystarburst/issues/453)
        # if partition_by:
        #     partition_columns = ", ".join(partition_by)
        #     partition_clause = f"PARTITION BY ({partition_columns})"

        clauses = [f"location => {convert_value_to_sql_option(location)}", f"format => {convert_value_to_sql_option(format)}"]

        if compression:
            clauses.append(f"compression => {convert_value_to_sql_option(compression)}")

        if separator:
            clauses.append(f"separator => {convert_value_to_sql_option(separator)}")

        if header is not None:
            header_value = "TRUE" if header else "FALSE"
            clauses.append(f"header => {header_value}")

        optional_clauses = ",\n".join(clauses)

        sql_query = f"""
        SELECT * FROM TABLE ({hive_catalog}.system.unload (
              input => TABLE ( {sub_query} ) {partition_clause},
              {optional_clauses}
            )
          )
        """.strip()

        self._dataframe._session.sql(sql_query).collect()
