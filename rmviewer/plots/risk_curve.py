import math

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from rmviewer.logger.custom_logger import Logger
from rmviewer.utils.figures import get_colors, update_figure, update_html

SPACING_DEFAULT = 0.05
MAX_ROW = 0.5
MIN_ROW = 0.1


def generate_risk_curve(var, context, rms=None, show_legend=False, rms_y=None):
    df_models = context["dataset"]
    groups = context["groups"]
    solution_id = context["solution_id"]

    groups = groups[(groups["SOLUTION_ID"] == solution_id) & (groups["VAR"] == var["x"])]

    models = groups.merge(
        df_models,
        left_on="MODEL_ID",
        right_on="ID",
        how="inner",
    )

    fig = go.Figure()

    rm_ids = groups["RM_ID"].drop_duplicates().tolist()
    colors = get_colors(rm_ids)
    color_by_rm = dict(zip(rm_ids, colors, strict=False))

    for rm_id, rm_models in models.groupby("RM_ID", sort=False):
        fig.add_trace(
            go.Scatter(
                x=rm_models[var["x"]],
                y=rm_models["CUMULATIVE_PROBABILITY"],
                mode="markers",
                marker={
                    "color": color_by_rm[rm_id],
                    "size": 4,
                },
                name=f"RM {rm_id}",
                legendgroup=f"RM_{rm_id}",
                showlegend=False,
            )
        )

    x_values = df_models.sort_values(by=var["x"])
    rms_x = x_values.loc[x_values["ID"].isin(rms)]
    rms_sorted = rms_x.sort_values(by=var["x"])

    sorted_colors = get_colors(rms_sorted["ID"])

    rms_x_sorted = rms_sorted[var["x"]].values

    if rms_y is not None:
        rms_y_sorted = rms_y.sort_values(by=var["x"], ascending=False)[var["x"]].values
    else:
        rms_y_sorted = []

    line_x, line_y = [], []
    marker_x, marker_y = [], []

    for i in range(len(rms_x_sorted)):
        x_val = rms_x_sorted[i]
        y_val = rms_y_sorted[i]

        if i == 0:
            line_x.append(x_val)
            line_y.append(1)
        else:
            prev_y_val = rms_y_sorted[i - 1]
            midpoint_prev_y = (y_val + prev_y_val) / 2

            line_x.append(x_val)
            line_y.append(midpoint_prev_y)

        line_x.append(x_val)
        line_y.append(y_val)

        if i < len(rms_x_sorted) - 1:
            next_y_val = rms_y_sorted[i + 1]
            midpoint_next_y = (y_val + next_y_val) / 2

            line_x.append(x_val)
            line_y.append(midpoint_next_y)
        else:
            line_x.append(x_val)
            line_y.append(0)

        marker_x.append(x_val)
        marker_y.append(y_val)

    fig.add_trace(
        go.Scatter(
            x=line_x,
            y=line_y,
            mode="lines",
            line={"color": "#888888", "width": 2},
            showlegend=show_legend,
            legendgroup="Lines",
            name="RMs curve",
        )
    )

    rms_points = [
        {
            "id": int(rm_id),
            "x": x,
            "y": y,
            "color": sorted_colors[i] if sorted_colors else "#FF6F00",
        }
        for i, (rm_id, x, y) in enumerate(
            zip(
                rms_sorted["ID"],
                marker_x,
                marker_y,
                strict=False,
            )
        )
    ]

    rms_points_sorted = sorted(rms_points, key=lambda point: point["id"])

    for point in rms_points_sorted:
        fig.add_trace(
            go.Scatter(
                x=[point["x"]],
                y=[point["y"]],
                mode="markers",
                marker={
                    "color": point["color"],
                    "size": 10,
                    "symbol": "circle",
                },
                showlegend=show_legend,
                name=f"RM {point['id']}",
                legendgroup=f"RM_{point['id']}",
            )
        )

    return fig


def add_figure(variables, fig, rms, sol_id, context):
    legend_shown = True
    context["solution_id"] = sol_id

    rms_y = context["rms_cumulative_prob"]
    rms_y = rms_y[rms_y["solution_id"] == sol_id]

    for var in variables:
        mini_fig = generate_risk_curve(
            var,
            rms=rms,
            context=context,
            show_legend=legend_shown,
            rms_y=rms_y,
        )

        for trace in mini_fig.data:
            fig.add_trace(trace, row=var["row"], col=var["col"])

        legend_shown = False

    return fig


def show_figure(rms, variables, params, context):
    values_columns = len(variables)
    rows = math.ceil(values_columns / 2)
    vertical_spacing = SPACING_DEFAULT

    if 1 / rows >= MAX_ROW:
        vertical_spacing = 0.1
    elif 1 / rows >= MIN_ROW:
        vertical_spacing = 0.05
    elif vertical_spacing >= (1 / (rows - 1)):
        vertical_spacing = 0.01
    else:
        vertical_spacing = 0.01

    fig = make_subplots(
        rows=rows,
        cols=2,
        vertical_spacing=vertical_spacing,
        horizontal_spacing=0.1,
    )

    fig = add_figure(variables, fig, rms, params["sol_id"], context)
    fig = update_figure(variables, fig, values_columns)

    total_height = max(500, rows * 500)
    fig.update_layout(height=total_height)

    name_file = "risk_curve.html"
    update_html(params["charts_path"], params["path_solutions"], fig, name_file)


def convert_list(variable_list):
    variables = []

    for index, item in enumerate(variable_list):
        row, col = divmod(index, 2)

        variables.append(
            {
                "x": item,
                "y": "acc",
                "row": row + 1,
                "col": col + 1,
                "title": f"{item}",
            }
        )

    return variables


def generate_risk_curve_chart(results, config):
    solution_ids = config["solution_ids"]
    charts_path = config["charts_path"]
    variables = [var.upper() for var in config["variables"]]

    models_cumulative_prob = config["models_cumulative_prob"]
    rms_cumulative_prob = config["rms_cumulative_prob"]
    dataset = config["dataset"]
    groups = config["groups"]

    context = {
        "models_cumulative_prob": models_cumulative_prob,
        "rms_cumulative_prob": rms_cumulative_prob,
        "dataset": dataset,
        "groups": groups,
    }

    df = results[results["solution_id"].isin(solution_ids)]

    path_solutions = [f"best_sol_{i + 1}_id_{sol_id}" for i, sol_id in enumerate(solution_ids)]

    variable_list = list(variables)

    rms = df.filter(regex="^RM")
    rms = rms.values.tolist()

    for index, sol_id in enumerate(solution_ids):
        variables_list = convert_list(variable_list)

        params = {
            "charts_path": charts_path,
            "path_solutions": path_solutions[index],
            "sol_id": sol_id,
        }

        show_figure(rms[index], variables_list, params, context)

    Logger().log_info(f"Risk curves generated in: {charts_path}")
