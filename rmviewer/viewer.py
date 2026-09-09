from pathlib import Path

import pandas as pd

from rmviewer.context.data_loader import load_time_series
from rmviewer.logger.custom_logger import Logger
from rmviewer.plots.attribute_levels import generate_attribute_levels_chart
from rmviewer.plots.convergence import convergence_chart
from rmviewer.plots.cross_plot import generate_cross_plot_chart
from rmviewer.plots.risk_curve import generate_risk_curve_chart
from rmviewer.plots.time_series import generate_time_series_chart
from rmviewer.utils.decorators import log_exceptions


class RMViewer:
    """
    Main class for Representative Model Viewer.
    """

    def __init__(
        self,
        solutions,
        dataset,
        solutions_results,
        time_series_path: Path | None = None,
    ):
        """
        Initializes the RMViewer class.

        Loads the solution IDs, the dataset and the optimization results.
        """
        self.solutions = solutions
        self.dataset = dataset
        self.solutions_results = solutions_results

        self.time_series = None

        if time_series_path is not None:
            self.time_series = load_time_series(time_series_path)

        Logger().log_info("Charts will be generated to visualize the results")

    @log_exceptions("Error generating cross plot")
    def generate_crossplot(
        self,
        variable_list: list[list[str]],
        prob_rms: pd.DataFrame,
        output_path: Path,
    ) -> None:
        """
        Generation of cross plot.

        :param variable_list: Pairs of variables to be plotted
        :param prob_rms: Probability of each representative model
        :param output_path: Path where files will be saved
        """
        config = {
            "dataset": self.dataset,
            "solutions": self.solutions,
            "variable_list": variable_list,
            "output_path": output_path,
            "prob_rms": prob_rms,
        }

        Logger().log_info(f"Generating crossplots with variables: {variable_list}")

        generate_cross_plot_chart(
            self.solutions_results,
            config,
        )

    @log_exceptions("Error generating risk curve")
    def generate_risk_curve(
        self,
        models_cumulative_prob: pd.DataFrame,
        rms_cumulative_prob: pd.DataFrame,
        output_path: Path,
        variables: list[str],
    ) -> None:
        """
        Generation of risk curve.

        :param models_cumulative_prob: Cumulative probability of models
        :param rms_cumulative_prob: Cumulative probability of RMs
        :param output_path: Path where files will be saved
        :param variables: List of variables to be plotted
        """
        config = {
            "solution_ids": self.solutions,
            "charts_path": output_path,
            "variables": variables,
            "models_cumulative_prob": models_cumulative_prob,
            "rms_cumulative_prob": rms_cumulative_prob,
            "dataset": self.dataset,
        }

        Logger().log_info(f"Generating risk curves with variables: {variables}")

        generate_risk_curve_chart(
            self.solutions_results,
            config,
        )

    @log_exceptions("Error generating histogram")
    def generate_histogram(
        self,
        results: pd.DataFrame,
        output_path: Path,
    ) -> None:
        """
        Generation of histogram.

        :param results: Result of the evaluation of the attribute level
        :param output_path: Path where files will be saved
        """
        Logger().log_info("Generating histograms")

        generate_attribute_levels_chart(
            self.solutions_results,
            self.solutions,
            results,
            output_path,
        )

    @log_exceptions("Error generating convergence chart")
    def generate_convergence_chart(
        self,
        output_path: Path,
        of_name: str = "of_value",
    ) -> None:
        """
        Generation of solution convergence chart.

        :param output_path: Path where files will be saved
        :param of_name: OF name from results file
        """
        Logger().log_info("Generating convergence chart")

        convergence_chart(
            self.solutions_results,
            output_path,
            of_name,
        )

    @log_exceptions("Error generating time series chart")
    def generate_time_series(
        self,
        variables: list[str],
        output_path: Path,
        rmsel_groups: pd.DataFrame,
    ) -> None:
        """
        Generation of time-series chart.

        :param variables: Variables to be plotted
        :param output_path: Path where files will be saved
        :param rmsel_groups: DataFrame containing the RMSel model groups
        """

        if self.time_series is None:
            raise ValueError("Time-series data was not provided.")

        data = {
            "solutions": self.solutions,
            "solutions_results": self.solutions_results,
            "variables": variables,
        }

        generate_time_series_chart(
            time_series=self.time_series,
            data=data,
            output_path=output_path,
            groups=rmsel_groups,
        )
