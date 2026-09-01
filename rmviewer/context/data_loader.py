import sys
from pathlib import Path
from typing import Any

from rmviewer import data_validation


def load_df(project_path: Path, relative_path: str):
    return data_validation.load_dataframe(project_path / relative_path)


def load_time_series(
    time_series_path: Path,
) -> dict[str, Any]:
    """
    Loads time-series data from a directory.
    Each CSV file represents one model.
    """
    if not time_series_path.is_dir():
        raise ValueError(f"Time-series path is not a directory: {time_series_path}")

    time_series = {}

    for file_path in sorted(time_series_path.glob("*.csv")):
        model_name = file_path.stem
        time_series[model_name] = data_validation.load_dataframe(file_path)

    if not time_series:
        raise ValueError(f"No CSV files found in time-series directory: {time_series_path}")

    return time_series


def load_data(config_path: Path) -> dict[str, Any]:
    """
    Loads the files and validates.

    :return: Dictionary with uploaded and validated files
    """
    config = data_validation.load_json(config_path)
    data_validation.validate_config(config)

    project_path_str = config.get("project_path")

    if not project_path_str:
        print("ERROR - It is necessary to include the project path.")
        sys.exit(1)

    project_path = Path(project_path_str)

    solutions = config.get("solutions", [])
    if not solutions:
        print("ERROR - No solutions provided in the configuration.")
        sys.exit(1)

    dataset = data_validation.load_dataframe(project_path / config["dataset"])

    solutions_results = data_validation.load_dataframe(project_path / config["solutions_results"])

    data = {
        "project_path": project_path,
        "config": config,
        "dataset": dataset,
        "solutions_results": solutions_results,
    }

    if time_series_path := config.get("time_series"):
        data["time_series"] = load_time_series(project_path / time_series_path)

    return data
