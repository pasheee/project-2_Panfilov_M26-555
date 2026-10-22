import json
from pathlib import Path


def load_metadata(filepath: str | Path) -> dict:
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError as e:
        print(f"warning: {e}")
        return {}


def save_metadata(filepath: str | Path, data: dict) -> None:
    with open(filepath, "w") as f:
        json.dump(data, f)
