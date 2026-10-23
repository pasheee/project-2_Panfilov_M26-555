from copy import deepcopy
from typing import Any, Iterable

from frozendict import frozendict

from .constants import CORRECT_TYPES, ID
from .decorators import confirm_action, handle_db_errors, log_time
from .errors import (
    ColumnDoesntExist,
    ColumnLengthError,
    ColumnTypeError,
    TableAlreadyExists,
    TableDoesntExist,
)
from .models import (
    Metadata,
    TableData,
    TableDataEnum,
    get_tmp_table,
)
from .utils import select_cache as _select_cache


def exit_programm(*args, **kwargs):
    """- выход из программы"""
    raise SystemExit(0)


def _validate_clause(clause: dict[str, Any], columns: Iterable[str]):
    for col in clause:
        if col not in columns:
            raise ColumnDoesntExist(f'Столбец "{col}" не существует.')


def _find_rows_idx(
    values: list[dict[str, Any]], where_clause: dict[str, Any]
) -> list[int]:
    return [
        i
        for i, row in enumerate(values)
        if all(row[col] == val for col, val in where_clause.items())
    ]


@handle_db_errors
def create_table(
    metadata: dict, table_name: str, columns: list[tuple[str, str]], **kwargs: Any
) -> Metadata:
    """<имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу"""
    if table_name in metadata:
        raise TableAlreadyExists(f'Таблица "{table_name}" уже существует.')

    seen = set()
    for name, column_type in columns:
        if column_type not in CORRECT_TYPES or (name == "ID" and column_type != "int"):
            raise ColumnTypeError(f"{name}:{column_type}")
        if name in seen:
            raise ColumnTypeError(f"повторный столбец {name}")
        seen.add(name)

    columns = [ID] + [column for column in columns if column[0] != "ID"]
    metadata[table_name] = {"schema": columns}
    schema = ", ".join(f"{name}:{column_type}" for name, column_type in columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {schema}')
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: dict, table_name: str, **kwargs: Any) -> Metadata:
    """<имя_таблицы> - удалить таблицу"""
    if table_name not in metadata:
        raise TableDoesntExist(f'Таблица "{table_name}" не существует.')

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


@handle_db_errors
def list_tables(metadata: Metadata, **kwargs: Any) -> Metadata:
    """- показать список всех таблиц"""
    if not metadata:
        print("Таблиц пока нет.")
    for table_name in metadata:
        print(f"- {table_name}")
    return metadata


def cast_values(values: dict[str, str], column_types: dict[str, str]) -> dict[str, Any]:
    _validate_clause(values, column_types)
    return {col: CORRECT_TYPES[column_types[col]](values[col]) for col in values}


@handle_db_errors
@log_time
def insert(
    metadata: Metadata, table_name: str, values: list[str], **kwargs: Any
) -> TableData:
    """into <таблица> values (...) - добавить запись"""
    if table_name not in metadata:
        raise TableDoesntExist(f'Таблица "{table_name}" не существует.')

    table_schema = metadata[table_name]["schema"]
    if len(values) != len(table_schema) - 1:
        raise ColumnLengthError(
            f"Values length {len(values)} != columns length {len(table_schema) - 1}"
        )

    column_names = [col for col, _ in table_schema]
    typed_values = cast_values(dict(zip(column_names[1:], values)), dict(table_schema))

    table_data = kwargs["table_data"]
    rows = table_data[TableDataEnum.VALUES.value]
    next_id = max((row["ID"] for row in rows), default=-1) + 1
    rows.append({"ID": next_id, **typed_values})
    print(f'Запись с ID={next_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


@handle_db_errors
@log_time
def select(
    table_data: TableData, where_clause: dict[str, Any] | None = None, **kwargs: Any
) -> TableData:
    """from <таблица> [where ...] - показать записи"""
    values = table_data[TableDataEnum.VALUES.value]
    columns = table_data[TableDataEnum.COLUMNS.value]
    table_name = table_data[TableDataEnum.TABLE_NAME.value]
    where_clause = where_clause or {}
    _validate_clause(where_clause, columns)

    def get_result() -> TableData:
        indices = _find_rows_idx(values, where_clause)
        tmp_table = get_tmp_table()
        tmp_table[TableDataEnum.COLUMNS.value] = columns.copy()
        tmp_table[TableDataEnum.VALUES.value] = [values[i].copy() for i in indices]
        return tmp_table

    key = (table_name, frozendict(where_clause))
    return deepcopy(_select_cache(key, get_result))


@handle_db_errors
@log_time
def update(
    table_data: TableData,
    set_clause: dict[str, Any],
    where_clause: dict[str, Any],
    **kwargs: Any,
) -> TableData:
    """<таблица> set <столбец> = <значение> where ... - обновить записи"""
    values = table_data[TableDataEnum.VALUES.value]
    table_name = table_data[TableDataEnum.TABLE_NAME.value]
    columns = table_data[TableDataEnum.COLUMNS.value]
    _validate_clause(set_clause, columns)
    _validate_clause(where_clause, columns)

    for i in _find_rows_idx(values, where_clause):
        row = values[i]
        row.update(set_clause)
        print(f'Запись с ID={row["ID"]} в таблице "{table_name}" успешно обновлена.')
    return table_data


@handle_db_errors
@confirm_action("удаление строк таблицы")
@log_time
def delete(
    table_data: TableData, where_clause: dict[str, Any], **kwargs: Any
) -> TableData:
    """from <таблица> where <столбец> = <значение> - удалить записи"""
    values = table_data[TableDataEnum.VALUES.value]
    table_name = table_data[TableDataEnum.TABLE_NAME.value]
    columns = table_data[TableDataEnum.COLUMNS.value]
    _validate_clause(where_clause, columns)

    for i in sorted(_find_rows_idx(values, where_clause), reverse=True):
        values[i], values[-1] = values[-1], values[i]
        row = values.pop()
        print(f'Запись с ID={row["ID"]} успешно удалена из таблицы "{table_name}".')
    return table_data


@handle_db_errors
def info(table_data: TableData, **kwargs: Any) -> None:
    """<таблица> - показывает информацию о таблице"""
    print(f"Таблица: {table_data[TableDataEnum.TABLE_NAME.value]}")
    columns_info = ", ".join(
        [
            col + ":" + str(val)
            for col, val in table_data[TableDataEnum.COLUMNS.value].items()
        ]
    )
    print(f"Столбцы: {columns_info}")
    print(f"Количество записей: {len(table_data[TableDataEnum.VALUES.value])}")
