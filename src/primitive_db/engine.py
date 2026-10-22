import shlex
from pathlib import Path
from typing import Callable

import prompt

from .core import (
    _parse_create_table,
    _parse_drop_table,
    create_table,
    drop_table,
    list_tables,
)
from .errors import ColumnTypeError, DatabaseError, ParseArgumentsError
from .utils import load_metadata, save_metadata

METADATA_FILEPATH = Path(__file__).resolve().parent / "meta.json"


def _help(*args, **kwargs):
    """- справочная информация"""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    for name, (command, _) in EXEC_COMMANDS.items():
        print(f"<command> {name} {command.__doc__}")
    print()
    return kwargs.get("metadata", {})


def _exit(*args, **kwargs):
    """- выход из программы"""
    raise SystemExit(0)


EXEC_COMMANDS: dict[str, tuple[Callable, Callable | None]] = {
    "create_table": (create_table, _parse_create_table),
    "list_tables": (list_tables, None),
    "drop_table": (drop_table, _parse_drop_table),
    "exit": (_exit, None),
    "help": (_help, None),
}


def welcome():
    _help()


def run():
    if not METADATA_FILEPATH.exists():
        METADATA_FILEPATH.write_text("{}", encoding="utf-8")

    welcome()
    while True:
        kwargs = {"metadata": load_metadata(METADATA_FILEPATH)}
        user_input = prompt.string(">>>Введите команду: ")
        if user_input is None:
            continue
        print()

        try:
            parts = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue
        if not parts:
            continue

        cmd_name = parts[0]
        try:
            command, parse_args = EXEC_COMMANDS[cmd_name]
        except KeyError:
            print(f"Функции {cmd_name} нет. Попробуйте снова.")
            continue

        try:
            if parse_args:
                kwargs.update(parse_args(parts[1:]))
            new_metadata = command(**kwargs)
        except (ParseArgumentsError, ColumnTypeError) as exc:
            print(f"Некорректное значение: {exc}. Попробуйте снова.")
            continue
        except DatabaseError as exc:
            print(f"Ошибка: {exc}")
            continue

        if cmd_name in {"create_table", "drop_table"}:
            save_metadata(METADATA_FILEPATH, new_metadata)


if __name__ == "__main__":
    run()
