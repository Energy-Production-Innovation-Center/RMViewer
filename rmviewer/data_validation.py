import json
import sys
from pathlib import Path

import pandas as pd


def validate_file(path: Path, extensions: str = ".csv") -> Path:
    """
    Validates if the file exists

    :param str path: Path to the file
    :param tuple extensions: Valid file extensions
    :return: Path object
    """
    file_path = Path(path)
    if not file_path.exists():
        print(f"ERROR - File not found:  {path}")
        sys.exit(1)
    if file_path.suffix not in extensions:
        print(f"ERROR - Invalid file extension: {path}")
        sys.exit(1)
    return file_path


def load_dataframe(path: Path) -> pd.DataFrame:
    """
    Load CSV into DataFrame with validation

    :param str path: CSV file path
    :return: Data loaded into DataFrame
    """
    file_path = validate_file(path, extensions=".csv")
    return pd.read_csv(file_path)


def load_json(path: Path) -> dict:
    """
    Load JSON with validation

    :param str path: JSON file path
    :return: Data loaded into dictionary
    """
    file_path = validate_file(path, extensions=".json")
    with file_path.open("r") as f:
        return json.load(f)


def _validate_required_keys(config: dict, required_keys: list[str]) -> None:
    """
    Validation of required fields fields for application execution

    :param dict config: Cofigurations from JSON file
    :param list required_keys: List of required fields
    """
    for key in required_keys:
        if key not in config:
            print(f"ERROR - Invalid configuration: Missing required key '{key}'")
            sys.exit(1)


def _validate_project_path(project_path: str) -> None:
    """
    Creates directory if the project paths does not exists.

    :param str project_path: Path to the project
    """

    path = Path(project_path)
    path.mkdir(parents=True, exist_ok=True)


def _validate_crossplot(config: dict, project_path: str) -> None:
    """
    Validates the configuration data for crossplot.

    :config: Cofigurations from JSON file
    :param str project_path: Path to the project
    """
    cross_plot = config["plot"]["crossplot"]
    if "variable_list" not in cross_plot or "prob_rms" not in cross_plot:
        print(
            "ERROR - Invalid configuration for crossplot: Requires 'variable_list' and 'prob_rms'"
        )
        sys.exit(1)
    prob_rms_path = Path(project_path) / cross_plot["prob_rms"]
    if not prob_rms_path.exists():
        print(f"ERROR - prob_rms file not found: {prob_rms_path}")
        sys.exit(1)

    if isinstance(cross_plot["variable_list"], list) and not isinstance(
        cross_plot["variable_list"][0], list
    ):
        cross_plot["variable_list"] = [cross_plot["variable_list"]]

    number_vars = 2
    if not isinstance(cross_plot["variable_list"], list) or not all(
        isinstance(item, list) and len(item) == number_vars for item in cross_plot["variable_list"]
    ):
        print(
            "ERROR - Invalid configuration for crossplot: 'variable_list' must be a list of pairs"
        )
        sys.exit(1)


def _validate_risk_curve(config: dict, project_path: str) -> None:
    """
    Validates the configuration data for risk curve.

    :config: Cofigurations from JSON file
    :param str project_path: Path to the project
    """

    risk_plot = config["plot"]["risk_curve"]
    if (
        "models_cumulative_prob" not in risk_plot
        or "rms_cumulative_prob" not in risk_plot
        or "variables" not in risk_plot
    ):
        print(
            "ERROR - Invalid configuration for risk_curve: Requires 'models_cumulative_prob', "
            "'rms_cumulative_prob' and 'variables'"
        )
        sys.exit(1)
    if not isinstance(risk_plot["variables"], list):
        print("ERROR - Invalid configuration for risk_curve: 'variables' must be a list")
        sys.exit(1)
    models_cp_path = Path(project_path) / risk_plot["models_cumulative_prob"]
    rms_cp_path = Path(project_path) / risk_plot["rms_cumulative_prob"]
    if not models_cp_path.exists():
        print(f"ERROR - models_cumulative_prob file not found: {models_cp_path}")
        sys.exit(1)
    if not rms_cp_path.exists():
        print(f"ERROR - rms_cumulative_prob file not found: {rms_cp_path}")
        sys.exit(1)


def _validate_histogram(config: dict) -> None:
    """
    Validates the configuration data for histogram.

    :config: Cofigurations from JSON file
    """
    hist_plot = config["plot"]["histogram"]
    if "results" not in hist_plot:
        print("ERROR - Invalid configuration for histogram: Missing 'results'")
        sys.exit(1)


def validate_solutions(config: dict) -> None:
    solutions = config.get("solutions", [])
    if not solutions:
        print("ERROR - No solutions provided in the configuration.")
        sys.exit(1)

    if not isinstance(solutions, list) or not all(isinstance(s, int) for s in solutions):
        print("ERROR - 'solutions' must be a list of integers.")
        sys.exit(1)


def validate_config(config: dict) -> None:
    """
    Validation of mandatory fields and values
    """
    required_keys = ["project_path", "solutions", "dataset", "solutions_results", "plot"]
    _validate_required_keys(config, required_keys)

    project_path = config.get("project_path", "")
    _validate_project_path(project_path)

    plot_cfg = config.get("plot", {})
    if "crossplot" in plot_cfg:
        _validate_crossplot(config, project_path)
    if "risk_curve" in plot_cfg:
        _validate_risk_curve(config, project_path)
    if "histogram" in plot_cfg:
        _validate_histogram(config)
