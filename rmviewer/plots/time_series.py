import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from rmviewer.logger.custom_logger import Logger
from rmviewer.utils.figures import get_colors, update_html

MODEL_COLOR = "#d3d3d3"
MODEL_WIDTH = 1
RM_WIDTH = 2.5


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
    Maps RMSel model IDs to the corresponding time-series models.
    """
    selected_models = []

    for rm in rms:
        for model_name, df in time_series.items():
            model_id = get_model_id(df)

            if model_id == rm:
                selected_models.append(model_name)
                break

    return selected_models


def add_model_traces(
    fig,
    time_series,
    variables,
    selected_models,
    colors,
):
    """
    Adds all model traces and highlights the RMSel representative models.
    """

    for index, variable in enumerate(variables):
        row = index
        col = 0

        for model_name, df in time_series.items():
            if variable not in df.columns:
                continue

            df_plot = prepare_time_series(df)

            fig.add_trace(
                go.Scatter(
                    x=df_plot["datetime"],
                    y=df_plot[variable],
                    mode="lines",
                    line={
                        "color": MODEL_COLOR,
                        "width": MODEL_WIDTH,
                    },
                    name="Models",
                    legendgroup="Models",
                    showlegend=(index == 0 and model_name == next(iter(time_series))),
                    hovertemplate=(
                        f"Model: {model_name}"
                        "<br>Date: %{x|%d/%m/%Y %H:%M:%S}"
                        f"<br>{variable}: %{{y}}"
                        "<extra></extra>"
                    ),
                ),
                row=row + 1,
                col=col + 1,
            )

    rm_index = 0
    for model_id, model_name in selected_models.items():
        rm_index += 1
        if model_name not in time_series:
            continue

        df_plot = prepare_time_series(time_series[model_name])

        for index, variable in enumerate(variables):
            if variable not in df_plot.columns:
                continue

            row = index
            col = 0

            fig.add_trace(
                go.Scatter(
                    x=df_plot["datetime"],
                    y=df_plot[variable],
                    mode="lines",
                    line={
                        "color": colors[rm_index - 1],
                        "width": RM_WIDTH,
                    },
                    name=f"RM {model_id}",
                    legendgroup=f"RM_{model_id}",
                    showlegend=index == 0,
                    hovertemplate=(
                        f"Model: {model_name}"
                        "<br>Date: %{x|%d/%m/%Y %H:%M:%S}"
                        f"<br>{variable}: %{{y}}"
                        "<extra></extra>"
                    ),
                ),
                row=row + 1,
                col=col + 1,
            )


def configure_figure(fig, variables):
    rows = len(variables)

    for index, variable in enumerate(variables):
        row = index
        col = 0

        fig.update_xaxes(
            title_text="Date",
            row=row + 1,
            col=col + 1,
            hoverformat="%d/%m/%Y %H:%M:%S",
        )

        fig.update_yaxes(
            title_text=variable,
            row=row + 1,
            col=col + 1,
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


def generate_time_series_plot(
    time_series,
    selected_models,
    variables,
    colors,
):
    """
    Generates the time-series figure.
    """

    rows = len(variables)

    fig = make_subplots(
        rows=rows,
        cols=1,
        subplot_titles=variables,
        vertical_spacing=max(0.05, 0.25 / rows),
    )

    add_model_traces(
        fig=fig,
        time_series=time_series,
        variables=variables,
        selected_models=selected_models,
        colors=colors,
    )

    return configure_figure(
        fig,
        variables,
    )


def generate_time_series_chart(
    time_series,
    solutions,
    solutions_results,
    variables,
    output_path,
):
    """
    Generates time-series charts highlighting RMSel
    representative models.
    """

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
            id_model: name_models[index] for index, id_model in enumerate(solution_rms)
        }

        colors = get_colors(solution_rms)

        fig = generate_time_series_plot(
            time_series=time_series,
            selected_models=selected_models,
            variables=variables,
            colors=colors,
        )

        solution_name = f"best_sol_{index + 1}_id_{solution_id}"

        update_html(
            output_path,
            solution_name,
            fig,
            "time_series.html",
        )

    Logger().log_info(f"Time-series charts generated in: {output_path}")
