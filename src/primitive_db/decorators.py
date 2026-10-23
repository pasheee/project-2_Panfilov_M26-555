import time
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

import prompt

from .errors import ColumnTypeError, DatabaseError, ParseArgumentsError

P = ParamSpec("P")
R = TypeVar("R")


def handle_db_errors(func: Callable[P, R]) -> Callable[P, R | None]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return func(*args, **kwargs)
        except (EOFError, KeyboardInterrupt):
            print()
            raise SystemExit(0)
        except (ColumnTypeError, ParseArgumentsError, TypeError, ValueError) as exc:
            print(f"Некорректное значение: {exc}. Попробуйте снова.")
        except (DatabaseError, KeyError, OSError) as exc:
            print(f"Ошибка: {exc}")
        return None

    return wrapper


def confirm_action(
    action_name: str,
) -> Callable[[Callable[P, R]], Callable[P, R | None]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R | None]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
            answer = prompt.secret(
                f"\nВы уверены, что хотите выполнить {action_name!r}? [y/n]: "
            )
            if answer == "y":
                return func(*args, **kwargs)
            print(f"Действие {action_name!r} отменено.")
            return None

        return wrapper

    return decorator


def log_time(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        print(f"Время выполнения {func.__name__}: {end - start:.6f} с")
        return result

    return wrapper
