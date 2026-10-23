from typing import Any

import prompt

from .constants import METADATA_FILEPATH
from .core import (
    create_table,
    delete,
    drop_table,
    exit_programm,
    info,
    insert,
    list_tables,
    select,
    update,
)
from .decorators import handle_db_errors
from .errors import ParseArgumentsError
from .models import ExecCommand, get_empty_table
from .parser import (
    parse_create_table,
    parse_delete,
    parse_drop_table,
    parse_info,
    parse_insert,
    parse_select,
    parse_update,
)
from .utils import (
    load_metadata,
    none_func,
    prepare_table,
    print_table,
    save_metadata,
    save_table_data,
)


def help_programm(**kwargs: Any) -> None:
    """справочная информация"""
    print("\n***Операции с данными***")
    print("Функции:")
    for name, entry in EXEC_COMMANDS.items():
        print(f"<command> {name} {entry['command'].__doc__ or ''}")
    print()


EXEC_COMMANDS: dict[str, ExecCommand] = {
    "list_tables": {
        "command": list_tables,
        "args_parser": None,
        "final_action": none_func,
    },
    "create_table": {
        "command": create_table,
        "args_parser": parse_create_table,
        "final_action": save_metadata,
    },
    "drop_table": {
        "command": drop_table,
        "args_parser": parse_drop_table,
        "final_action": save_metadata,
    },
    "help": {"command": help_programm, "args_parser": None, "final_action": none_func},
    "exit": {"command": exit_programm, "args_parser": None, "final_action": none_func},
    "insert": {
        "command": insert,
        "args_parser": parse_insert,
        "final_action": save_table_data,
    },
    "select": {
        "command": select,
        "args_parser": parse_select,
        "final_action": print_table,
    },
    "delete": {
        "command": delete,
        "args_parser": parse_delete,
        "final_action": save_table_data,
    },
    "update": {
        "command": update,
        "args_parser": parse_update,
        "final_action": save_table_data,
    },
    "info": {
        "command": info,
        "args_parser": parse_info,
        "final_action": none_func,
    },
}


@handle_db_errors
def execute_command(user_input: str) -> None:
    parts = user_input.split(maxsplit=1)
    if not parts:
        return

    entry = EXEC_COMMANDS.get(parts[0])
    if entry is None:
        print(f"Функции {parts[0]} нет. Попробуйте снова.")
        return

    raw_args = parts[1] if len(parts) > 1 else ""
    command = entry["command"]
    parse_args = entry["args_parser"]
    final_action = entry["final_action"]

    if parse_args is None and raw_args.strip():
        raise ParseArgumentsError(f"Failed to parse {raw_args}")

    metadata = load_metadata(METADATA_FILEPATH)
    kwargs = parse_args(raw_args, metadata) if parse_args else {}
    table_name = kwargs.get("table_name")

    table_data = get_empty_table()
    if table_name is not None and table_name in metadata:
        table_data = prepare_table(table_name, dict(metadata[table_name]["schema"]))

    result = command(metadata=metadata, table_data=table_data, **kwargs)
    if result is not None:
        final_action(result)


@handle_db_errors
def run():
    if not METADATA_FILEPATH.exists():
        METADATA_FILEPATH.write_text("{}", encoding="utf-8")

    help_programm()
    while True:
        user_input = prompt.string(">>>Введите команду: ", empty=True)
        if user_input is None:
            continue
        print()
        execute_command(user_input)


if __name__ == "__main__":
    run()
