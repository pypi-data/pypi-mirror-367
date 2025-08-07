#
# Copyright (c) Starburst Data, Inc. All rights reserved.
#

from typing import Dict, List, Optional, Union

import pystarburst
from pystarburst._internal.utils import TempObjectType, random_name_for_temp_object


class ResultCache:
    """A context manager that creates temp table to cache results and drops them on exit."""

    def __init__(
        self,
        session: "pystarburst.session.Session",
        database_name: str,
        schema_name: str,
        table_properties: Dict[str, Union[str, bool, int, float]],
        statement_properties: Optional[Dict[str, str]],
    ) -> None:
        self.session = session
        self.database_name = database_name
        self.schema_name = schema_name
        self.table_properties = table_properties
        self.statement_properties = statement_properties

        self._tables: List["pystarburst.Table"] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for table in self._tables:
            table.drop_table()

    def cache(self, original: "pystarburst.DataFrame") -> "pystarburst.Table":
        table_name = random_name_for_temp_object(TempObjectType.TABLE)
        if self.database_name is not None and self.schema_name is not None:
            table_name = [self.database_name, self.schema_name, table_name]

        original.write.save_as_table(
            table_name=table_name,
            mode="errorifexists",
            table_properties=self.table_properties,
            statement_properties=self.statement_properties,
        )
        table = self.session.table(table_name)
        self._tables.append(table)
        return table
