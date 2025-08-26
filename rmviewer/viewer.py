from rmviewer.logger.custom_logger import Logger
from rmviewer.plots.attribute_levels import generate_attribute_levels_chart
from rmviewer.plots.convergence import convergence_chart
from rmviewer.plots.cross_plot import generate_cross_plot_chart
from rmviewer.plots.risk_curve import generate_risk_curve_chart


class RMViewer:
    """
    Main class for Representative Model Viewer.
    """

    def __init__(self, solutions=None, dataset=None, solutions_results=None):
        """
        Initializes the RMViewer class.
        """
        self.solutions = solutions
        self.dataset = dataset
        self.solutions_results = solutions_results

        Logger().log_info("Graphs will be generated to visualize the results of the best solutions")

    def generate_crossplot(self, variable_list, prob_rms, output_path):
        try:
            generate_cross_plot_chart(
                self.solutions_results,
                self.dataset,
                self.solutions,
                variable_list,
                output_path,
                prob_rms,
            )
        except Exception as ex:
            Logger().log_error(f"Error generating cross plot chart: {ex}")

    def generate_risk_curve(
        self, models_cumulative_prob, rms_cumulative_prob, output_path, variables
    ) -> None:
        config = {
            "solution_ids": self.solutions,
            "charts_path": output_path,
            "variables": variables,
            "models_cumulative_prob": models_cumulative_prob,
            "rms_cumulative_prob": rms_cumulative_prob,
            "dataset": self.dataset,
        }
        try:
            generate_risk_curve_chart(self.solutions_results, config)
        except Exception as ex:
            Logger().log_error(f"Error generating risk curve chart: {ex}")

    def generate_histogram(self, results, output_path) -> None:
        try:
            generate_attribute_levels_chart(
                self.solutions_results, self.solutions, results, output_path
            )
        except Exception as ex:
            Logger().log_error(f"Error generating attribute level chart: {ex}")

    def generate_convergence_chart(self, output_path):
        try:
            convergence_chart(self.solutions_results, output_path)
        except Exception as ex:
            Logger().log_error(f"Error generating convergence chart: {ex}")
