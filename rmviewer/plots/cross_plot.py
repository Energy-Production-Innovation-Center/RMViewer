import math

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from rmviewer.logger.custom_logger import Logger
from rmviewer.plots.utils import get_colors, update_figure, update_html

MAX_MARKER = 20
MIN_MARKER = 10


def get_size_markers(list_prob):
    min_prob = min(list_prob)
    max_prob = max(list_prob)

    size_markers = []
    for prob in list_prob:
        if max_prob == min_prob:
            size_markers.append(MIN_MARKER)
        else:
            size_markers.append(
                MIN_MARKER + (prob - min_prob) * (MAX_MARKER - MIN_MARKER) / (max_prob - min_prob)
            )

    return size_markers


def generate_cross_plot(params, rms, showlegend, solution_id):
    x_values = params["df"][params["x"]]
    y_values = params["df"][params["y"]]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=y_values,
            mode="markers",
            marker={"color": "black", "size": 4},
            name="Models",
            legendgroup="Models",
            showlegend=showlegend,
        )
    )

    rms_x = [x_values[i] for i in rms]
    rms_y = [y_values[i] for i in rms]

    rms_probability = [
        rm
        for sol, rm in zip(
            params["probability_list"]["solution_id"],
            params["probability_list"]["probability"],
            strict=False,
        )
        if sol == solution_id
    ]
    sorted_colors = get_colors(rms)
    size_markers = get_size_markers(rms_probability)

    for i, (x_val, y_val) in enumerate(zip(rms_x, rms_y, strict=False)):
        fig.add_trace(
            go.Scatter(
                x=[x_val],
                y=[y_val],
                mode="markers",
                marker={
                    "color": sorted_colors[i] if sorted_colors else "#FF6F00",
                    "size": size_markers[i] if size_markers else 10,
                    "symbol": "circle",
                },
                showlegend=showlegend,
                name=f"RM {rms[i]}",
                legendgroup=f"RM_{rms[i]}",
            )
        )

    return fig


def add_figure(vars_, fig, rms, solution_id, config):
    legend_shown = True

    for var in vars_:
        params = {
            "x": var["x"],
            "y": var["y"],
            "df": config["dataset"],
            "probability_list": config["probability_list"],
        }
        mini_fig = generate_cross_plot(params, rms, legend_shown, solution_id)

        for trace in mini_fig.data:
            fig.add_trace(trace, row=var["row"], col=var["col"])

        legend_shown = False

    return fig


def show_figure(rms, vars_, charts_path, info_solutions, config):
    values_columns = len(vars_)
    rows = math.ceil(values_columns / 2)
    fig = make_subplots(
        rows=math.ceil(values_columns / 2),
        cols=2,
        subplot_titles=[var["title"] for var in vars_],
        vertical_spacing=max(0.05, 0.25 / rows),
        horizontal_spacing=0.1,
    )
    fig = add_figure(vars_, fig, rms, info_solutions[1], config)
    fig = update_figure(vars_, fig, values_columns)

    name_file = "cross_plot.html"
    update_html(charts_path, info_solutions[0], fig, name_file)


def convert_list(variable_list):
    vars_ = []

    for index, item in enumerate(variable_list):
        x, y = item

        row, col = divmod(index, 2)

        vars_.append(
            {
                "x": x,
                "y": y,
                "row": row + 1,
                "col": col + 1,
                "title": f"{x} vs {y}",
            }
        )

    return vars_


def generate_cross_plot_chart(
    results, dataset, solutions_ids, variable_list, charts_path, probability_list
):  # noqa: PLR0913
    df_rm = results[results["solution_id"].isin(solutions_ids)]

    path_solutions = [f"best_sol_{i + 1}_id_{id_}" for i, id_ in enumerate(solutions_ids)]

    rms = df_rm.filter(regex="^RM")
    rms = rms.values.tolist()
    config = {"dataset": dataset, "probability_list": probability_list}

    for index, solution in enumerate(solutions_ids):
        list_vars = convert_list(variable_list)
        show_figure(
            rms[index],
            list_vars,
            charts_path,
            (path_solutions[index], solution),
            config,
        )

    Logger().log_info(f"The cross plot graphs were generated in: {charts_path}")
