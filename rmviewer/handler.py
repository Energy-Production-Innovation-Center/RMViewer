from pathlib import Path

from rmviewer.context.data_loader import load_data, load_df
from rmviewer.viewer import RMViewer


def call_viewer(config_path: Path) -> None:
    """
    Prepare the data for execution.

    :param config_path: Dictionary with execution configuration
    """

    data = load_data(config_path)
    config = data.get("config")

    if config is None:
        raise ValueError("'config' key is required in data.")

    project_data = data.get("project_path")
    assert project_data is not None

    project_path = Path(project_data)

    solutions = config.get("solutions")
    dataset = data.get("dataset")
    solutions_results = data.get("solutions_results")
    time_series = data.get("time_series")

    plots = config.get("plot", {})

    viewer = RMViewer(
        solutions=solutions,
        dataset=dataset,
        solutions_results=solutions_results,
        time_series=time_series,
    )

    results_path = project_path / "charts"

    if cross_plot := plots.get("crossplot"):
        prob_rms = load_df(
            project_path,
            cross_plot["prob_rms"],
        )

        viewer.generate_crossplot(
            variable_list=cross_plot["variable_list"],
            prob_rms=prob_rms,
            output_path=results_path,
        )

    if risk_curve_plot := plots.get("risk_curve"):
        models_cumulative_prob = load_df(
            project_path,
            risk_curve_plot["models_cumulative_prob"],
        )

        rms_cumulative_prob = load_df(
            project_path,
            risk_curve_plot["rms_cumulative_prob"],
        )

        viewer.generate_risk_curve(
            models_cumulative_prob=models_cumulative_prob,
            rms_cumulative_prob=rms_cumulative_prob,
            output_path=results_path,
            variables=risk_curve_plot["variables"],
        )

    if hist_plot := plots.get("histogram"):
        results = load_df(
            project_path,
            hist_plot["results"],
        )

        viewer.generate_histogram(
            results=results,
            output_path=results_path,
        )

    if convergence_plot := plots.get("convergence"):
        viewer.generate_convergence_chart(
            output_path=results_path,
            of_name=convergence_plot["of_name"],
        )

    if time_series_plot := plots.get("time_series"):
        if time_series is None:
            raise ValueError(
                "Time-series configuration was provided, but no time-series data was loaded."
            )

        viewer.generate_time_series(
            variables=time_series_plot["variables"],
            output_path=results_path,
        )
