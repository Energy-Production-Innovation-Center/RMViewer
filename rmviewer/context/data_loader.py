import sys
from pathlib import Path
from typing import Any

from rmviewer import data_validation


def load_df(project_path: Path, relative_path: str):
    return data_validation.load_dataframe(project_path / relative_path)


def load_data(config_path: Path) -> dict[str, Any]:
    """
    Loads the files and validates

    :return: Dictionary with uploaded and validated files
    """
    config = data_validation.load_json(config_path)
    data_validation.validate_config(config)

    project_path = Path(config.get("project_path"))

    solutions = config.get("solutions", [])
    if not solutions:
        print("ERROR - No solutions provided in the configuration.")
        sys.exit(1)

    dataset = data_validation.load_dataframe(project_path / config["dataset"])
    solutions_results = data_validation.load_dataframe(project_path / config["solutions_results"])

    return {
        "project_path": project_path,
        "config": config,
        "dataset": dataset,
        "solutions_results": solutions_results,
    }
