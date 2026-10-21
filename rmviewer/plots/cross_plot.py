import math

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from rmviewer.logger.custom_logger import Logger
from rmviewer.utils.figures import get_colors, update_figure, update_html

MAX_MARKER = 20
MIN_MARKER = 10


def get_size_markers(list_prob):
    if not list_prob:
        return []

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


def get_models_by_ids(df, model_ids):
    """
    Returns the original models identified by MODEL_ID.

    If the dataset has an ID column, it is used to match models.
    Otherwise, MODEL_ID is assumed to be 1-based and correspond
    to the row position in the dataset.
    """
    if "ID" in df.columns:
        return df[df["ID"].isin(model_ids)]

    positions = [int(model_id) - 1 for model_id in model_ids if 1 <= int(model_id) <= len(df)]

    return df.iloc[positions]


def get_solution_groups(groups, solution_id):
    """
    Returns the original models grouped by RM_ID for a solution.
    """
    required_columns = {"SOLUTION_ID", "MODEL_ID", "RM_ID"}
    missing_columns = required_columns - set(groups.columns)

    if missing_columns:
        raise ValueError(f"Groups dataframe is missing required columns: {sorted(missing_columns)}")

    solution_groups = groups[groups["SOLUTION_ID"] == solution_id]

    if solution_groups.empty:
        return {}

    return solution_groups.groupby("RM_ID")["MODEL_ID"].apply(list).to_dict()


def add_models_by_rm(fig, params, rms, solution_id):
    """
    Adds the original models using the color of their representative RM.
    """
    df = params["df"]
    groups = params["groups"]

    solution_groups = get_solution_groups(groups, solution_id)

    colors = get_colors(rms)

    color_by_rm = {rm_id: colors[index] for index, rm_id in enumerate(rms) if index < len(colors)}

    assigned_models = set()

    for rm_id, model_ids in solution_groups.items():
        models = get_models_by_ids(df, model_ids)

        if models.empty:
            continue

        color = color_by_rm.get(rm_id, "black")

        fig.add_trace(
            go.Scatter(
                x=models[params["x"]],
                y=models[params["y"]],
                mode="markers",
                marker={
                    "color": color,
                    "size": 4,
                },
                name=f"Models RM {rm_id}",
                legendgroup=f"RM_{rm_id}",
                showlegend=False,
                hovertemplate=(
                    "Model ID: %{customdata}"
                    f"<br>RM: {rm_id}"
                    f"<br>{params['x']}: %{{x}}"
                    f"<br>{params['y']}: %{{y}}"
                    "<extra></extra>"
                ),
                customdata=(models["ID"] if "ID" in models.columns else models.index + 1),
            )
        )

        assigned_models.update(model_ids)

    # Models not associated with a representative remain black.
    all_model_ids = df["ID"].tolist() if "ID" in df.columns else list(range(1, len(df) + 1))

    unassigned_ids = set(all_model_ids) - assigned_models - set(rms)

    if unassigned_ids:
        models = get_models_by_ids(df, unassigned_ids)

        if not models.empty:
            fig.add_trace(
                go.Scatter(
                    x=models[params["x"]],
                    y=models[params["y"]],
                    mode="markers",
                    marker={"color": "black", "size": 4},
                    name="Other models",
                    legendgroup="Models",
                    showlegend=False,
                )
            )


def generate_cross_plot(params, rms, showlegend, solution_id):
    df = params["df"]

    fig = go.Figure()

    # Original models are colored according to their representative RM.
    add_models_by_rm(fig, params, rms, solution_id)

    colors = get_colors(rms)

    rms_probability = [
        probability
        for sol, probability in zip(
            params["probability_list"]["solution_id"],
            params["probability_list"]["probability"],
            strict=False,
        )
        if sol == solution_id
    ]

    size_markers = get_size_markers(rms_probability)

    for index, rm_id in enumerate(rms):
        model = get_models_by_ids(df, [rm_id])

        if model.empty:
            Logger().log_warning(f"Representative model ID={rm_id} not found in dataset.")
            continue

        x_val = model[params["x"]].iloc[0]
        y_val = model[params["y"]].iloc[0]

        fig.add_trace(
            go.Scatter(
                x=[x_val],
                y=[y_val],
                mode="markers",
                marker={
                    "color": (colors[index] if index < len(colors) else "#FF6F00"),
                    "size": (size_markers[index] if index < len(size_markers) else MIN_MARKER),
                },
                showlegend=showlegend,
                name=f"RM {rm_id}",
                legendgroup=f"RM_{rm_id}",
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
            "groups": config["groups"],
        }

        mini_fig = generate_cross_plot(
            params,
            rms,
            legend_shown,
            solution_id,
        )

        for trace in mini_fig.data:
            fig.add_trace(
                trace,
                row=var["row"],
                col=var["col"],
            )

        legend_shown = False

    return fig


def show_figure(rms, vars_, charts_path, info_solutions, config):
    values_columns = len(vars_)
    rows = math.ceil(values_columns / 2)

    vertical_spacing = min(0.25 / rows, 1 / (rows - 1)) if rows > 1 else 0

    fig = make_subplots(
        rows=rows,
        cols=2,
        subplot_titles=[var["title"] for var in vars_],
        vertical_spacing=vertical_spacing,
        horizontal_spacing=0.1,
    )

    fig = add_figure(
        vars_,
        fig,
        rms,
        info_solutions[1],
        config,
    )

    fig = update_figure(vars_, fig, values_columns)

    name_file = "cross_plot.html"

    update_html(
        charts_path,
        info_solutions[0],
        fig,
        name_file,
    )


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


def generate_cross_plot_chart(results, config):
    dataset = config.get("dataset")
    solutions_ids = config.get("solutions")
    groups = config.get("groups")

    variable_list = config.get("variable_list")
    variable_list = [[var.upper() for var in pair_vars] for pair_vars in variable_list]

    charts_path = config.get("output_path")
    probability_list = config.get("prob_rms")

    if groups is None:
        raise ValueError("The 'groups' DataFrame must be provided in config.")

    df_rm = results[results["solution_id"].isin(solutions_ids)]

    path_solutions = [
        f"best_sol_{index + 1}_id_{solution_id}" for index, solution_id in enumerate(solutions_ids)
    ]

    rms = df_rm.filter(regex="^RM")
    rms = rms.values.tolist()

    config = {
        "dataset": dataset,
        "probability_list": probability_list,
        "groups": groups,
    }

    for index, solution in enumerate(solutions_ids):
        list_vars = convert_list(variable_list)

        show_figure(
            rms[index],
            list_vars,
            charts_path,
            (path_solutions[index], solution),
            config,
        )

    Logger().log_info(f"Crossplots generated in: {charts_path}")
