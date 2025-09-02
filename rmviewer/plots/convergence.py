from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from rmviewer.logger.custom_logger import Logger


def generate_fig(df, show_legend=False, of_name="of_value"):
    df = df.sort_values(by="solution_id").reset_index(drop=True)

    selected = [df.iloc[0]]
    for i in range(1, len(df)):
        if df.iloc[i][of_name] < selected[-1][of_name]:
            selected.append(df.iloc[i])

    df_selected = pd.DataFrame(selected)

    iterations = df_selected["solution_id"]
    of_value = df_selected[of_name]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=iterations,
            y=of_value,
            mode="lines+markers",
            line={"color": "#003C71", "width": 4},
            marker={"color": "#003C71", "size": 5},
            name="Evolution of the objective function",
            showlegend=show_legend,
        )
    )

    return fig


def add_figure(vars_, fig, df, of_name):
    legend = True
    for _var in vars_:
        mini_fig = generate_fig(df, show_legend=legend, of_name=of_name)

        for trace in mini_fig.data:
            fig.add_trace(trace)

        legend = False

    return fig


def update_figure(vars_, fig):
    for var in vars_:
        fig.update_layout(
            title=var["title"],
            title_x=0.5,
        )
        fig.update_xaxes(title_text="solutions")
        fig.update_yaxes(title_text="of_value")

    fig.update_layout(
        autosize=True,
        margin={"l": 50, "r": 50, "t": 50, "b": 50},
        showlegend=True,
        plot_bgcolor="#fafafa",
        paper_bgcolor="#fafafa",
    )
    return fig


def show_figure(variables, df, charts_path, of_name):
    fig = make_subplots(rows=1, cols=1)
    fig = add_figure(variables, fig, df, of_name)
    fig = update_figure(variables, fig)

    path_html = charts_path / Path("solutions_convergence.html")
    fig.write_html(path_html, full_html=True)

    Logger().log_info(f"Convergence chart generated in: {path_html}")


def convergence_chart(df, charts_path, of_name):
    variables = [
        {
            "title": "Convergence of the Optimization Method",
        },
    ]

    show_figure(variables, df, charts_path, of_name)
