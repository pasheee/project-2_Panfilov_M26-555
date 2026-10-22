from typing import Any

from .errors import (
    ColumnTypeError,
    ParseArgumentsError,
    TableAlreadyExists,
    TableDoesntExist,
)

CORRECT_TYPES = {"int", "str", "bool"}
ID = ("ID", "int")


def _parse_create_table(args: list[str]) -> dict[str, Any]:
    if len(args) < 2 or not args[0]:
        raise ParseArgumentsError(" ".join(args) or "(пустые аргументы)")

    columns = []
    for column in args[1:]:
        parts = column.split(":")
        if len(parts) != 2 or not all(parts):
            raise ParseArgumentsError(column)
        columns.append((parts[0], parts[1]))

    return {"table_name": args[0], "columns": columns}


def _parse_drop_table(args: list[str]) -> dict[str, str]:
    if len(args) != 1 or not args[0]:
        raise ParseArgumentsError(" ".join(args) or "(пустые аргументы)")

    return {"table_name": args[0]}


def create_table(
    metadata: dict, table_name: str, columns: list[tuple[str, str]]
) -> dict:
    """<имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу"""
    if table_name in metadata:
        raise TableAlreadyExists(f'Таблица "{table_name}" уже существует.')

    for name, column_type in columns:
        if column_type not in CORRECT_TYPES or (name == "ID" and column_type != "int"):
            raise ColumnTypeError(f"{name}:{column_type}")
    if sum(name == "ID" for name, _ in columns) > 1:
        raise ColumnTypeError("повторный столбец ID")

    columns = [ID] + [column for column in columns if column[0] != "ID"]
    metadata[table_name] = {"schema": columns}
    schema = ", ".join(f"{name}:{column_type}" for name, column_type in columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {schema}')
    return metadata


def drop_table(metadata: dict, table_name: str) -> dict:
    """<имя_таблицы> - удалить таблицу"""
    if table_name not in metadata:
        raise TableDoesntExist(f'Таблица "{table_name}" не существует.')

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata: dict) -> dict:
    """- показать список всех таблиц"""
    if not metadata:
        print("Таблиц пока нет.")
    for table_name in metadata:
        print(f"- {table_name}")
    return metadata
