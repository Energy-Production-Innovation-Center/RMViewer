from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from rmviewer.logger.custom_logger import Logger
from rmviewer.utils.figures import get_html_centered_content


def generate_histogram(df_rm, charts_path, path_solutions):
    df_rm = df_rm.reset_index(drop=True)

    model_frequencies = df_rm.filter(regex="^MODEL_FREQUENCY").columns
    rms_frequencies = df_rm.filter(regex="^RMS_FREQUENCY").columns

    num_plots = len(df_rm)

    fig = make_subplots(
        rows=num_plots,
        cols=1,
        subplot_titles=df_rm["Variable"].to_list(),
        shared_xaxes=False,
    )

    show_legend_model = True
    show_legend_rms = True

    for i, row in df_rm.iterrows():
        model_values = row[model_frequencies].dropna().values
        rms_values = row[rms_frequencies].dropna().values

        x_axis_values = list(range(1, len(model_values) + 1))

        fig.add_trace(
            go.Bar(
                x=x_axis_values,
                y=model_values,
                name="MODEL Frequencies",
                marker={"color": "#FF6F00"},
                opacity=0.6,
                showlegend=show_legend_model,
                legendgroup="model_frequencies",
                offsetgroup=0,
            ),
            row=i + 1,
            col=1,
        )

        fig.add_trace(
            go.Bar(
                x=x_axis_values,
                y=rms_values,
                name="RMS Frequencies",
                marker={"color": "#003C71"},
                opacity=0.6,
                showlegend=show_legend_rms,
                legendgroup="rms_frequencies",
                offsetgroup=1,
            ),
            row=i + 1,
            col=1,
        )

        show_legend_model = False
        show_legend_rms = False

        fig.update_xaxes(
            tickvals=x_axis_values,
            ticktext=[str(i) for i in x_axis_values],
            title_text="Levels",
            row=i + 1,
            col=1,
        )

        fig.update_yaxes(title_text="Frequency", row=i + 1, col=1)

    fig.update_layout(
        barmode="group",
        legend_title="Frequency Type",
        plot_bgcolor="#fafafa",
        height=300 * num_plots,
        width=800,
        margin={"l": 50, "r": 50, "t": 50, "b": 50},
        showlegend=True,
    )

    config = {"displayModeBar": True, "scrollZoom": True}

    path = charts_path / Path(path_solutions)
    path.mkdir(parents=True, exist_ok=True)
    html_path = path / Path("attribute_levels.html")
    fig.write_html(html_path, config=config)

    with Path(html_path).open(encoding="utf-8") as file:
        content = file.read()

    centered_content = get_html_centered_content(content, width="800px")

    with Path(html_path).open("w", encoding="utf-8") as file:
        file.write(centered_content)


def generate_attribute_levels_chart(dataset, solutions, results, output_path):
    df_of = results

    df_rms = dataset[dataset["solution_id"].isin(solutions)]

    path_solutions = [f"best_sol_{i + 1}_id_{id_}" for i, id_ in enumerate(solutions)]

    for i, rm in enumerate(df_rms["solution_id"].to_list()):
        df_rm = df_of[df_of["SOLUTION_ID"].isin([rm])]
        generate_histogram(df_rm, output_path, path_solutions[i])

    Logger().log_info(f"Attribute-level histograms generated in: {output_path}")
