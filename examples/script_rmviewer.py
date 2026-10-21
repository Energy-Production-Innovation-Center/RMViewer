from pathlib import Path

import pandas as pd
from rmviewer import RMViewer

# Directory to save the output
charts_path = Path("/Documentos/project/") / "charts"
charts_path.mkdir(parents=True, exist_ok=True)

df = pd.read_csv("/Documentos/project/solutions.csv")
solutions_ids = [4962]
dataset_normalization = pd.read_csv("/Documentos/project/database_normalization.csv")

rmviewer = RMViewer(solutions=solutions_ids, dataset=dataset_normalization, solutions_results=df)

# Setting up a crossplot
rmviewer.generate_convergence_chart(charts_path)
variable_list = [["NPV", "WP"], ["NP", "WP"]]
probability_list = pd.read_csv("/Documentos/project/rms_probabilities.csv")
rmsel_groups = pd.read_csv("/Documentos/project/cross_plot_objective_function.csv")

rmviewer.generate_crossplot(
    variable_list=variable_list,
    prob_rms=probability_list,
    output_path=charts_path,
    rmsel_groups=rmsel_groups,
)

# Setting up a risk curve
models_cumulative_prob = pd.read_csv("/Documentos/project/cumulative_probability.csv")
rms_cumulative_prob = pd.read_csv("/Documentos/project/rms_cumulative_prob.csv")
risk_curve_results = pd.read_csv("/Documentos/project/risk_curve_objective_function.csv")
variable_list = ["NPV", "NP", "WP", "ORF"]

rmviewer.generate_risk_curve(
    models_cumulative_prob=models_cumulative_prob,
    rms_cumulative_prob=rms_cumulative_prob,
    output_path=charts_path,
    variables=variable_list,
    risk_curve_results=risk_curve_results,
)

# Setting up a histogram
attribute_results = pd.read_csv(
    "/Documentos/test_viewer/test1/attribute_levels_objective_function.csv"
)
rmviewer.generate_histogram(attribute_results, charts_path)
