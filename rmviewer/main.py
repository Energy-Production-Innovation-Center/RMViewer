import argparse
import sys
from pathlib import Path

from rmviewer import data_validation
from rmviewer.viewer import RMViewer


def _get_argument():
    parser = argparse.ArgumentParser(
        description="Representative Model Viewer",
    )
    parser.add_argument("--config_view", type=str, required=True, help="Path to config file (JSON)")
    return parser


def parse_args():
    parser = _get_argument()
    return parser.parse_args()


def main():
    args = parse_args()

    config_path = Path(args.config_view)
    if not config_path.exists():
        print(f"ERROR - Config file not found: {config_path}")
        sys.exit(1)

    config = data_validation.load_json(config_path)
    data_validation.validate_config(config)

    solutions = config.get("solutions", [])
    dataset = data_validation.load_dataframe(config["dataset"])
    solutions_results = data_validation.load_dataframe(config["solutions_results"])
    plots = config.get("plot", {})

    viewer = RMViewer(
        solutions=solutions,
        dataset=dataset,
        solutions_results=solutions_results,
    )

    if "crossplot" in plots:
        cross_cfg = plots["crossplot"]
        prob_rms = data_validation.load_dataframe(cross_cfg["prob_rms"])
        viewer.generate_crossplot(
            variable_list=cross_cfg["variable_list"],
            prob_rms=prob_rms,
            output_path=cross_cfg["output_path"],
        )

    if "risk_curve" in plots:
        risk_cfg = plots["risk_curve"]
        models_cumulative_prob = data_validation.load_dataframe(risk_cfg["models_cumulative_prob"])
        rms_cumulative_prob = data_validation.load_dataframe(risk_cfg["rms_cumulative_prob"])
        viewer.generate_risk_curve(
            models_cumulative_prob=models_cumulative_prob,
            rms_cumulative_prob=rms_cumulative_prob,
            output_path=risk_cfg["output_path"],
            variables=risk_cfg["variables"],
        )

    if "histogram" in plots:
        hist_cfg = plots["histogram"]
        results = data_validation.load_dataframe(hist_cfg["results"])
        viewer.generate_histogram(
            results=results,
            output_path=hist_cfg["output_path"],
        )

    if "convergence" in plots:
        conv_cfg = plots["convergence"]
        viewer.generate_convergence_chart(
            output_path=conv_cfg["output_path"],
        )


if __name__ == "__main__":
    main()
