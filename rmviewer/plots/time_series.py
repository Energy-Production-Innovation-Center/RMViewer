import pandas as pd
import plotly.graph_objects as go
from plotly.colors import hex_to_rgb
from plotly.subplots import make_subplots
from rmviewer.logger.custom_logger import Logger
from rmviewer.utils.figures import get_colors, update_html

MODEL_COLOR = "#d3d3d3"
MODEL_WIDTH = 1
RM_WIDTH = 2.5


def hex_to_rgba(color, alpha=0.25):
    if color.startswith("rgb"):
        values = color[color.find("(") + 1 : color.find(")")].split(",")
        red, green, blue = [int(value.strip()) for value in values[:3]]
    else:
        red, green, blue = hex_to_rgb(color)

    return f"rgba({red}, {green}, {blue}, {alpha})"


def prepare_time_series(df):
    """
    Prepares the time-series dataframe for plotting.
    """
    df = df.copy()

    if "Date" not in df.columns:
        raise ValueError("Time-series dataframe must contain a 'Date' column.")

    date_values = df["Date"].astype(str).str.strip()

    if "Time" in df.columns:
        date_values = date_values + " " + df["Time"].astype(str).str.strip()

    df["datetime"] = pd.to_datetime(
        date_values,
        format="mixed",
        errors="raise",
    )

    return df.sort_values("datetime")


def get_model_id(df):
    """
    Returns the model ID from the time-series dataframe.
    """
    if "ID" not in df.columns:
        raise ValueError("Time-series dataframe must contain an 'ID' column.")

    return df["ID"].iloc[0]


def get_selected_models(time_series, rms):
    """
    Maps RMSel representative model IDs to the corresponding
    time-series model names.
    """
    selected_models = []

    for rm in rms:
        for model_name, df in time_series.items():
            model_id = get_model_id(df)

            if model_id == rm:
                selected_models.append(model_name)
                break

    return selected_models


def get_model_name_by_id(time_series, model_id):
    """
    Returns the time-series model name corresponding to a MODEL_ID.
    """
    for model_name, df in time_series.items():
        if get_model_id(df) == model_id:
            return model_name

    return None


def get_solution_groups(groups, solution_id):
    """
    Returns the models grouped by RM for a specific solution.
    """

    required_columns = {
        "SOLUTION_ID",
        "MODEL_ID",
        "RM_ID",
    }

    missing_columns = required_columns - set(groups.columns)

    if missing_columns:
        raise ValueError(f"Groups dataframe is missing required columns: {sorted(missing_columns)}")

    solution_groups = groups[groups["SOLUTION_ID"] == solution_id].copy()

    if solution_groups.empty:
        return {}

    return solution_groups.groupby("RM_ID")["MODEL_ID"].apply(list).to_dict()


def prepare_group_timeseries(
    time_series,
    model_ids,
    variable,
):
    """
    Prepares the time series of all models belonging to one RM group.
    """

    series_list = []

    for model_id in model_ids:
        model_name = get_model_name_by_id(
            time_series,
            model_id,
        )

        if model_name is None:
            Logger().log_warning(f"MODEL_ID={model_id} not found in time_series.")
            continue

        df = prepare_time_series(time_series[model_name])

        if variable not in df.columns:
            continue

        series = df[["datetime", variable]].copy()

        series = series.rename(columns={variable: f"model_{model_id}"})

        series_list.append(series)

    if not series_list:
        return None

    result = series_list[0]

    for series in series_list[1:]:
        result = result.merge(
            series,
            on="datetime",
            how="outer",
        )

    return result.sort_values("datetime")


def add_coalesced_group(fig, time_series, model_ids, variable, params_fig):
    """
    Adds the coalesced representation of a group.

    The group is represented by a min/max envelope.

    The envelope itself has no hover information.
    """
    row, col, color = params_fig["row"], params_fig["col"], params_fig["color"]
    group_df = prepare_group_timeseries(
        time_series=time_series,
        model_ids=model_ids,
        variable=variable,
    )

    if group_df is None:
        return

    model_columns = [column for column in group_df.columns if column.startswith("model_")]

    if not model_columns:
        return

    group_df["group_min"] = group_df[model_columns].min(axis=1)

    group_df["group_max"] = group_df[model_columns].max(axis=1)

    fig.add_trace(
        go.Scatter(
            x=group_df["datetime"],
            y=group_df["group_min"],
            mode="lines",
            line={
                "color": color,
                "width": 0,
            },
            hoverinfo="skip",
            showlegend=False,
        ),
        row=row,
        col=col,
    )

    fig.add_trace(
        go.Scatter(
            x=group_df["datetime"],
            y=group_df["group_max"],
            mode="lines",
            line={
                "color": color,
                "width": 0,
            },
            fill="tonexty",
            fillcolor=hex_to_rgba(color, 0.25),
            hoverinfo="skip",
            showlegend=False,
        ),
        row=row,
        col=col,
    )


def add_rm_trace(time_series, model_name, rm_id, params_fig):
    """
    Adds the representative model trace.

    This is the only trace that contains hover information.
    """
    row, col, color = params_fig["row"], params_fig["col"], params_fig["color"]
    fig, variable = params_fig["fig"], params_fig["variable"]

    if model_name not in time_series:
        return

    df_plot = prepare_time_series(time_series[model_name])

    if variable not in df_plot.columns:
        return

    fig.add_trace(
        go.Scatter(
            x=df_plot["datetime"],
            y=df_plot[variable],
            mode="lines",
            line={
                "color": color,
                "width": RM_WIDTH,
            },
            name=f"RM {rm_id}",
            legendgroup=f"RM_{rm_id}",
            showlegend=row == 1,
            hovertemplate=(
                f"RM: {rm_id}"
                f"<br>Model: {model_name}"
                "<br>Date: %{x|%d/%m/%Y %H:%M:%S}"
                f"<br>{variable}: %{{y}}"
                "<extra></extra>"
            ),
        ),
        row=row,
        col=col,
    )


def add_model_traces(fig, time_series, groups, solution_id, extra):
    """
    Adds the coalesced groups and representative model traces.
    """
    variables = extra.get("variables")
    selected_models = extra.get("selected_models")
    colors = extra.get("colors")

    solution_groups = get_solution_groups(
        groups,
        solution_id,
    )

    if not solution_groups:
        Logger().log_warning(f"No groups found for solution_id={solution_id}")
        return

    for index, variable in enumerate(variables):
        row = index + 1
        col = 1

        for rm_index, (_, model_ids) in enumerate(solution_groups.items()):
            if rm_index >= len(colors):
                break

            color = colors[rm_index]
            params_fig = {"row": row, "col": col, "color": color}
            add_coalesced_group(
                fig=fig,
                time_series=time_series,
                model_ids=model_ids,
                variable=variable,
                params_fig=params_fig,
            )

    for rm_index, (rm_id, model_name) in enumerate(selected_models.items()):
        if rm_index >= len(colors):
            break

        if model_name not in time_series:
            continue

        color = colors[rm_index]

        for index, variable in enumerate(variables):
            params_fig = {
                "fig": fig,
                "color": color,
                "row": index + 1,
                "col": 1,
                "variable": variable,
            }

            add_rm_trace(
                time_series=time_series,
                model_name=model_name,
                rm_id=rm_id,
                params_fig=params_fig,
            )


def configure_figure(fig, variables):
    """
    Configures the Plotly figure.
    """

    rows = len(variables)

    for index, variable in enumerate(variables):
        row = index + 1
        col = 1

        fig.update_xaxes(
            title_text="Date",
            row=row,
            col=col,
            hoverformat="%d/%m/%Y %H:%M:%S",
        )

        fig.update_yaxes(
            title_text=variable,
            row=row,
            col=col,
        )

    height = 600 * rows
    width = 1200

    fig.update_layout(
        height=height,
        width=width,
        margin={
            "l": 70,
            "r": 70,
            "t": 70,
            "b": 70,
        },
        autosize=True,
        showlegend=True,
        plot_bgcolor="#fafafa",
        hovermode="x unified",
    )

    return fig


def generate_time_series_plot(time_series, groups, solution_id, extra):
    """
    Generates the time-series figure with coalesced groups
    and highlighted RMSel representative models.
    """
    selected_models = extra.get("selected_models")
    variables = extra.get("variables")
    colors = extra.get("colors")

    rows = len(variables)

    fig = make_subplots(
        rows=rows,
        cols=1,
        subplot_titles=variables,
        vertical_spacing=max(
            0.05,
            0.25 / rows,
        ),
    )

    extra = {"variables": variables, "selected_models": selected_models, "colors": colors}

    add_model_traces(
        fig=fig, time_series=time_series, groups=groups, solution_id=solution_id, extra=extra
    )

    return configure_figure(
        fig,
        variables,
    )


def generate_time_series_chart(time_series, data, output_path, groups) -> None:
    """
    Generates time-series charts highlighting RMSel
    representative models and coalescing the models
    belonging to each representative group.
    """
    solutions = data.get("solutions")
    solutions_results = data.get("solutions_results")
    variables = data.get("variables")

    for index, solution_id in enumerate(solutions):
        solution_result = solutions_results[solutions_results["solution_id"] == solution_id]

        if solution_result.empty:
            Logger().log_warning(f"No results found for solution_id={solution_id}")
            continue

        solution_rms = solution_result.filter(regex="^RM").iloc[0].dropna().tolist()

        name_models = get_selected_models(
            time_series,
            solution_rms,
        )

        selected_models = {
            rm_id: name_models[index]
            for index, rm_id in enumerate(solution_rms)
            if index < len(name_models)
        }

        colors = get_colors(solution_rms)

        extra = {"selected_models": selected_models, "variables": variables, "colors": colors}
        fig = generate_time_series_plot(
            time_series=time_series, groups=groups, solution_id=solution_id, extra=extra
        )

        solution_name = f"best_sol_{index + 1}_id_{solution_id}"

        update_html(
            output_path,
            solution_name,
            fig,
            "time_series.html",
        )

    Logger().log_info(f"Time-series charts generated in: {output_path}")
