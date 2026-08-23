import random

from dash import Dash, dcc, html
from components import create_bar_figure, create_line_figure


def generate_sample_data() -> tuple[list[str], list[int], list[int]]:
    labels = [f"P{i}" for i in range(1, 13)]
    line_values = [random.randint(20, 100) for _ in labels]
    bar_values = [random.randint(10, 90) for _ in labels]
    return labels, line_values, bar_values


def create_app() -> Dash:
    labels, line_values, bar_values = generate_sample_data()
    line_fig = create_line_figure(labels, line_values)
    bar_fig = create_bar_figure(labels, bar_values)

    app = Dash(__name__)
    app.layout = html.Div(
        style={"maxWidth": "1200px", "margin": "20px auto", "padding": "0 16px"},
        children=[
            html.H1("Financeinator Client Dashboard"),
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px"},
                children=[dcc.Graph(figure=line_fig), dcc.Graph(figure=bar_fig)],
            ),
        ],
    )
    return app


def run() -> None:
    app = create_app()
    app.run(host="127.0.0.1", port=8050, debug=False)


if __name__ == "__main__":
    run()
