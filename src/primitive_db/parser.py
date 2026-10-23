import json
import shlex
from typing import Any

from .core import cast_values
from .errors import ParseArgumentsError, TableDoesntExist
from .models import Metadata


def _shlex_split(raw_args: str) -> list[str]:
    try:
        return shlex.split(raw_args)
    except ValueError as exc:
        raise ParseArgumentsError(raw_args) from exc


def parse_create_table(raw_args: str, metadata: Metadata) -> dict[str, Any]:
    args = _shlex_split(raw_args)

    if len(args) < 2 or not args[0]:
        raise ParseArgumentsError(" ".join(args) or "(empty arguments)")

    columns = []
    for column in args[1:]:
        parts = column.split(":")
        if len(parts) != 2 or not all(parts):
            raise ParseArgumentsError(column)
        columns.append((parts[0], parts[1]))

    return {"table_name": args[0], "columns": columns}


def parse_drop_table(raw_args: str, metadata: Metadata) -> dict[str, str]:
    args = _shlex_split(raw_args)

    if len(args) != 1 or not args[0]:
        raise ParseArgumentsError(" ".join(args) or "(empty arguments)")

    return {"table_name": args[0]}


def parse_insert(raw_args: str, metadata: Metadata) -> dict[str, Any]:
    args = raw_args.split(maxsplit=3)
    if len(args) != 4 or args[0] != "into" or args[2] != "values":
        raise ParseArgumentsError(f"Failed to parse {args}")

    expression = args[3].strip()
    if expression.startswith("(") and expression.endswith(")"):
        expression = f"[{expression[1:-1]}]"

    try:
        values = json.loads(expression)
    except json.JSONDecodeError as e:
        raise ParseArgumentsError(f"Failed to parse {args}: {e}") from e

    if not isinstance(values, list):
        raise ParseArgumentsError(f"Failed to parse {args}: expected a list of values")

    values = [
        str(value).lower() if isinstance(value, bool) else str(value)
        for value in values
    ]
    return {"table_name": args[1], "values": values}


def parse_select(raw_args: str, metadata: Metadata) -> dict[str, Any]:
    args = _shlex_split(raw_args)

    if len(args) not in (2, 6) or args[0] != "from":
        raise ParseArgumentsError(f"Failed to parse {args}")
    if len(args) == 6 and (args[2] != "where" or args[4] != "="):
        raise ParseArgumentsError(f"Failed to parse {args}")

    table_name = args[1]
    if table_name not in metadata:
        raise TableDoesntExist(f'Таблица "{table_name}" не существует.')
    if len(args) == 2:
        return {"table_name": table_name}

    column_types = dict(metadata[table_name]["schema"])
    where_clause = cast_values({args[3]: args[5]}, column_types)
    return {"table_name": table_name, "where_clause": where_clause}


def parse_update(raw_args: str, metadata: Metadata) -> dict[str, Any]:
    args = _shlex_split(raw_args)

    if (
        len(args) != 9
        or args[1] != "set"
        or args[3] != "="
        or args[5] != "where"
        or args[7] != "="
    ):
        raise ParseArgumentsError(f"Failed to parse {args}")

    table_name = args[0]
    if table_name not in metadata:
        raise TableDoesntExist(f'Таблица "{table_name}" не существует.')
    column_types = dict(metadata[table_name]["schema"])
    return {
        "table_name": table_name,
        "set_clause": cast_values({args[2]: args[4]}, column_types),
        "where_clause": cast_values({args[6]: args[8]}, column_types),
    }


def parse_delete(raw_args: str, metadata: Metadata) -> dict[str, Any]:
    args = _shlex_split(raw_args)

    if len(args) != 6 or args[0] != "from" or args[2] != "where" or args[4] != "=":
        raise ParseArgumentsError(f"Failed to parse {args}")

    table_name = args[1]
    if table_name not in metadata:
        raise TableDoesntExist(f'Таблица "{table_name}" не существует.')
    column_types = dict(metadata[table_name]["schema"])
    return {
        "table_name": table_name,
        "where_clause": cast_values({args[3]: args[5]}, column_types),
    }


def parse_info(raw_args: str, metadata: Metadata) -> dict[str, Any]:
    args = _shlex_split(raw_args)

    if len(args) != 1 or not args[0]:
        raise ParseArgumentsError(f"Failed to parse {args}")

    table_name = args[0]
    if table_name not in metadata:
        raise TableDoesntExist(f'Таблица "{table_name}" не существует.')

    return {"table_name": table_name}
