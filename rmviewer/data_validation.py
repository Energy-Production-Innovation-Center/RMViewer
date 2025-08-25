import json
from pathlib import Path

import pandas as pd


def validate_file(path: str, extensions=(".csv", ".json")) -> Path:
    """Validates if the file exists"""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    return file_path


def load_dataframe(path: str) -> pd.DataFrame:
    """Load CSV into DataFrame with validation"""
    file_path = validate_file(path, extensions=(".csv",))
    return pd.read_csv(file_path)


def load_json(path: str) -> dict:
    """Load JSON with validation"""
    file_path = validate_file(path, extensions=(".json",))
    with open(file_path, "r") as f:
        return json.load(f)


def validate_config(config: dict) -> None:
    """Validates if the configuration JSON has the primary keys"""
    required_keys = ["solutions", "dataset", "solutions_results", "plot"]
    for key in required_keys:
        if key not in config:
            raise KeyError(f"Invalid configuration: Missing required key '{key}'")
