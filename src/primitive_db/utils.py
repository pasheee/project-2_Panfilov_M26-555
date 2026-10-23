import json
from pathlib import Path
from typing import Any, Callable, Hashable, TypeVar

from prettytable import PrettyTable

from .constants import METADATA_FILEPATH, TABLE_DATA_PATH
from .models import (
    Metadata,
    TableData,
    TableDataEnum,
    get_empty_metadata,
    get_empty_table,
)

R = TypeVar("R")

type CacheKey = tuple[str, Hashable]


def load_metadata(filepath: str | Path) -> Metadata:
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError as e:
        print(f"warning: {e}")
        return get_empty_metadata()


def save_metadata(data: dict, filepath: str | Path = METADATA_FILEPATH) -> None:
    previous = load_metadata(filepath) if Path(filepath).exists() else {}
    with open(filepath, "w") as f:
        json.dump(data, f)
    for table_name in previous.keys() | data.keys():
        if previous.get(table_name) != data.get(table_name):
            clear_select_cache(table_name)


def load_table_data(table_name: str) -> TableData:
    filepath = TABLE_DATA_PATH / f"{table_name}.json"
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return get_empty_table()


def save_table_data(data: TableData) -> None:
    filepath = TABLE_DATA_PATH / f"{data[TableDataEnum.TABLE_NAME.value]}.json"

    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f)
    clear_select_cache(data[TableDataEnum.TABLE_NAME.value])


def print_table(table_data: TableData) -> None:
    values = table_data[TableDataEnum.VALUES.value]
    columns = table_data[TableDataEnum.COLUMNS.value]
    if not values:
        print("Нет данных.")
        return

    table = PrettyTable(list(columns.keys()))
    table.add_rows([[row[col] for col in columns] for row in values])
    print(table)
    return


def prepare_table(table_name: str, columns: dict[str, str]) -> TableData:
    table_data = load_table_data(table_name)
    if not table_data[TableDataEnum.TABLE_NAME.value]:
        table_data[TableDataEnum.TABLE_NAME.value] = table_name
        table_data[TableDataEnum.COLUMNS.value] = columns.copy()
    return table_data


def none_func(*args, **kwargs) -> None:
    return None


def create_cacher() -> tuple[
    Callable[[CacheKey, Callable[[], R]], R], Callable[[str], None]
]:
    cache: dict[str, dict[Hashable, Any]] = {}

    def cacher(key: CacheKey, func: Callable[[], R]) -> R:
        table_name, condition = key
        table_cache = cache.setdefault(table_name, {})
        if condition not in table_cache:
            table_cache[condition] = func()
        return table_cache[condition]

    def clear(table_name: str) -> None:
        cache.pop(table_name, None)

    return cacher, clear


select_cache, clear_select_cache = create_cacher()
