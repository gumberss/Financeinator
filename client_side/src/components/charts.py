import plotly.graph_objects as go


def create_line_figure(labels: list[str], values: list[float]) -> go.Figure:
    line_fig = go.Figure(
        data=[
            go.Scatter(
                x=labels,
                y=values,
                mode="lines+markers",
                name="Line",
                line={"shape": "spline", "smoothing": 0.3, "width": 2},
                marker={"size": 7},
            )
        ]
    )
    line_fig.update_layout(title="Line Graph", template="plotly_white")
    return line_fig


def create_bar_figure(labels: list[str], values: list[float]) -> go.Figure:
    bar_fig = go.Figure(
        data=[
            go.Bar(
                x=labels,
                y=values,
                name="Bars",
                marker={
                    "color": "rgba(99, 150, 237, 0.78)",
                    "line": {"color": "rgba(99, 150, 237, 0.38)", "width": 1.5},
                },
            )
        ]
    )
    bar_fig.update_layout(
        title="Bar Graph",
        template="plotly_white",
        bargap=0.28,
        barcornerradius=5,
    )
    return bar_fig


def create_type_month_comparison_figure(
    month_labels: list[str],
    types: list[str],
    values_by_type: dict[str, list[float]],
) -> go.Figure:
    fig = go.Figure()

    for transaction_type in types:
        fig.add_trace(
            go.Bar(
                x=month_labels,
                y=values_by_type.get(transaction_type, [0.0] * len(month_labels)),
                name=transaction_type,
            )
        )

    fig.update_layout(
        title="Spent by Type per Month (Last 6 Months)",
        template="plotly_white",
        barmode="group",
        bargap=0.22,
        barcornerradius=5,
        legend_title_text="Type",
        yaxis_title="Amount",
        xaxis_title="Month",
    )
    return fig
