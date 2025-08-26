import math
from pathlib import Path

import plotly.colors as p_colors


def get_html_centered_content(content, width="1200px"):
    return f"""
    <html>
    <head>
        <style>
            body {{
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
            }}
            .plotly-container {{
                text-align: center;
                width: {width};
                height: auto;
            }}
        </style>
    </head>
    <body>
        <div class="plotly-container">
            {content}
        </div>
    </body>
    </html>
    """


def update_figure(vars_, fig, values_columns):
    for var in vars_:
        fig.update_xaxes(title_text=var["x"], row=var["row"], col=var["col"])
        fig.update_yaxes(title_text=var["y"], row=var["row"], col=var["col"])

    columns = 2
    rows = math.ceil(values_columns / columns)

    height = 600 * rows
    width = 1200

    fig.update_layout(
        height=height,
        width=width,
        margin={"l": 70, "r": 70, "t": 70, "b": 70},
        autosize=True,
        showlegend=True,
        plot_bgcolor="#fafafa",
    )

    return fig


def update_html(charts_path, path_solutions, fig, name_file):
    path = charts_path / Path(path_solutions)
    path.mkdir(parents=True, exist_ok=True)

    config = {"displayModeBar": True, "scrollZoom": True}

    html_path = path / Path(name_file)
    fig.write_html(html_path, config=config)

    with Path(html_path).open(encoding="utf-8") as file:
        content = file.read()

    centered_content = get_html_centered_content(content)

    with Path(html_path).open("w", encoding="utf-8") as file:
        file.write(centered_content)


def get_colors(rms) -> list:
    plotly_colors = (
        p_colors.qualitative.Safe
        + p_colors.qualitative.Plotly
        + p_colors.qualitative.Set2
        + p_colors.qualitative.Dark2
    )
    plotly_colors = list(dict.fromkeys(plotly_colors))

    if len(rms) > len(plotly_colors):
        return []

    dic_colors = {rm_id: plotly_colors[index] for index, rm_id in enumerate(sorted(rms))}
    return [dic_colors[rm_id] for rm_id in rms]
