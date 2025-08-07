#
# Copyright (c) 2012-2022 Snowflake Computing Inc. All rights reserved.
# Copyright (c) Starburst Data, Inc. All rights reserved.
#

import re
from typing import Optional, Union

from pystarburst._internal.error_message import PyStarburstClientExceptionMessages
from pystarburst._internal.utils import is_single_quoted, validate_object_name

SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'
EMPTY_STRING = ""


def convert_value_to_sql_option(value: Optional[Union[str, bool, int, float]]) -> str:
    if isinstance(value, str):
        if len(value) > 1 and is_single_quoted(value):
            return value
        else:
            value = value.replace("'", "''")  # escape single quotes before adding a pair of quotes
            return f"'{value}'"
    else:
        return str(value)


def single_quote(value: str) -> str:
    if value.startswith(SINGLE_QUOTE) and value.endswith(SINGLE_QUOTE):
        return value
    else:
        return SINGLE_QUOTE + value + SINGLE_QUOTE


ALREADY_QUOTED = re.compile('^(".+")$')
UNQUOTED_CASE_INSENSITIVE = re.compile("^([_A-Za-z]+[_A-Za-z0-9$]*)$")


def quote_name(name: str) -> str:
    if ALREADY_QUOTED.match(name):
        return validate_quoted_name(name)
    else:
        return DOUBLE_QUOTE + escape_quotes(name.lower()) + DOUBLE_QUOTE


def quote_table_qualified_identifier(name: str) -> str:
    """
    quotes table qualified identifiers, which could be passed in a forms:
        - table or "table"
        - schema.table or "schema"."table"
        - catalog.schema.table or "catalog"."schema"."table"
    """
    qualified_table_name_list = validate_object_name(name)
    quoted_qualified_table_name_list = [quote_name(i) for i in qualified_table_name_list]
    quoted_qualified_table_name = ".".join(quoted_qualified_table_name_list)
    return quoted_qualified_table_name


def validate_quoted_name(name: str) -> str:
    if DOUBLE_QUOTE in name[1:-1].replace(DOUBLE_QUOTE + DOUBLE_QUOTE, EMPTY_STRING):
        raise PyStarburstClientExceptionMessages.PLAN_ANALYZER_INVALID_IDENTIFIER(name)
    else:
        return name


def escape_quotes(unescaped: str) -> str:
    return unescaped.replace(DOUBLE_QUOTE, DOUBLE_QUOTE + DOUBLE_QUOTE)
