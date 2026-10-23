from enum import StrEnum
from typing import Any, Callable, TypedDict


def gen():
    """генерирует номера временных таблиц"""
    id = 0
    while True:
        yield id
        id += 1


class TableData(TypedDict):
    table_name: str
    columns: dict[str, str]
    values: list[dict[str, Any]]


class TableDataEnum(StrEnum):
    TABLE_NAME = "table_name"
    COLUMNS = "columns"
    VALUES = "values"


class TableMetadata(TypedDict):
    schema: list[list[str]]


type Metadata = dict[str, TableMetadata]


class ExecCommand(TypedDict):
    command: Callable
    args_parser: Callable[[str, Metadata], dict[str, Any]] | None
    final_action: Callable


tmp_id_gen = gen()


def get_tmp_table() -> TableData:
    """создаёт временную таблицу"""
    tmp_table: TableData = {
        TableDataEnum.TABLE_NAME.value: f"tmp_{next(tmp_id_gen)}",
        TableDataEnum.COLUMNS.value: {},
        TableDataEnum.VALUES.value: [],
    }

    return tmp_table


def get_empty_table() -> TableData:
    """создаёт пустые данные таблицы"""
    empty_table_data: TableData = {
        TableDataEnum.TABLE_NAME.value: "",
        TableDataEnum.COLUMNS.value: {},
        TableDataEnum.VALUES.value: [],
    }
    return empty_table_data


def get_empty_metadata() -> Metadata:
    """создаёт пустые метаданные"""
    empty_metadata: Metadata = {}
    return empty_metadata
