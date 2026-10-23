from pathlib import Path

METADATA_FILEPATH = Path(__file__).resolve().parent / "meta.json"
TABLE_DATA_PATH = Path(__file__).resolve().parent / "data"
ID = ("ID", "int")


def _bool(val: str):
    """преобразует true или false в bool"""
    if val == "true":
        return True
    if val == "false":
        return False

    raise TypeError(f"Value {val!r} should be false or true")


CORRECT_TYPES = {"int": int, "str": str, "bool": _bool}
