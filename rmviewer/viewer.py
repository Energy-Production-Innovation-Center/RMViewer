import pandas as pd
from pathlib import Path
from rmviewer.logger.custom_logger import Logger
from rmviewer.plots.attribute_levels import generate_attribute_levels_chart
from rmviewer.plots.convergence import convergence_chart
from rmviewer.plots.cross_plot import generate_cross_plot_chart
from rmviewer.plots.risk_curve import generate_risk_curve_chart
from rmviewer.utils.decorators import log_exceptions


class RMViewer:
    """
    Main class for Representative Model Viewer.
    """

    def __init__(self, solutions=None, dataset=None, solutions_results=None):
        """
        Initializes the RMViewer class.

        Loads the solution IDs, the dataset and the optimization results.

        """
        self.solutions = solutions
        self.dataset = dataset
        self.solutions_results = solutions_results

        Logger().log_info("Graphs will be generated to visualize the results")

    @log_exceptions("Error generating cross plot chart")
    def generate_crossplot(
        self, variable_list: list[list[str]], prob_rms: pd.DataFrame, output_path: Path
    ) -> None:
        """
        Generation of cross plot graphs.

        :param list variable_list: Pairs of variables to be plotted
        :param dataframe prob_rms: Probability of each representative model
        :param path output_path: Path where files will be saved
        """
        config = {
            "dataset": self.dataset,
            "solutions": self.solutions,
            "variable_list": variable_list,
            "output_path": output_path,
            "prob_rms": prob_rms,
        }
        Logger().log_info(f"Generating crossplot with variables: {variable_list}")

        generate_cross_plot_chart(self.solutions_results, config)

    @log_exceptions("Error generating risk curve chart")
    def generate_risk_curve(
        self,
        models_cumulative_prob: pd.DataFrame,
        rms_cumulative_prob: pd.DataFrame,
        output_path: Path,
        variables: list[str],
    ) -> None:
        """
        Generation of risk curve graphs.

        :param dataframe models_cumulative_prob: Cumulative probability of models
        :param dataframe rms_cumulative_prob: Cumulative probability of RMs
        :param path output_path: Path where files will be saved
        :param list variable_list: List of variables to be plotted
        """
        config = {
            "solution_ids": self.solutions,
            "charts_path": output_path,
            "variables": variables,
            "models_cumulative_prob": models_cumulative_prob,
            "rms_cumulative_prob": rms_cumulative_prob,
            "dataset": self.dataset,
        }
        Logger().log_info(f"Generating risk curve with variables: {variables}")

        generate_risk_curve_chart(self.solutions_results, config)

    @log_exceptions("Error generating attribute level chart")
    def generate_histogram(self, results: pd.DataFrame, output_path: Path) -> None:
        """
        Generation of histogram graphs.

        :param dataframe results: Result of the evaluation of the attribute level
        :param path output_path: Path where files will be saved
        """
        Logger().log_info("Generating histogram chart")

        generate_attribute_levels_chart(
            self.solutions_results, self.solutions, results, output_path
        )

    @log_exceptions("Error generating convergence chart")
    def generate_convergence_chart(self, output_path: Path, of_name: str = "of_value") -> None:
        """
        Generation of solution convergence graphs.

        :param path output_path: Path where files will be saved
        :param str of_value: OF name from results file
        """
        Logger().log_info(f"Generating convergence chart")

        convergence_chart(self.solutions_results, output_path, of_name)
