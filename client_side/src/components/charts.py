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


def create_donut_figure(
    labels: list[str],
    values: list[float],
    title: str,
) -> go.Figure:
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.48,
                texttemplate="%{label}<br>%{value:.2f}<br>%{percent}",
                hovertemplate="%{label}<br>Amount: %{value:.2f}<br>Percentage: %{percent}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title=title,
        template="plotly_white",
        legend_title_text="Group",
    )
    return fig


def create_type_month_comparison_figure(
    month_labels: list[str],
    types: list[str],
    values_by_type: dict[str, list[float]],
    month_count: int,
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
        title=f"Spent by Type per Month (Last {month_count} Month{'s' if month_count != 1 else ''})",
        template="plotly_white",
        barmode="group",
        bargap=0.22,
        barcornerradius=5,
        legend_title_text="Type",
        yaxis_title="Amount",
        xaxis_title="Month",
    )
    return fig


def create_month_over_month_diff_figure(
    month_labels: list[str],
    types: list[str],
    diffs_by_type: dict[str, list[float]],
    month_count: int,
) -> go.Figure:
    fig = go.Figure()

    for transaction_type in types:
        fig.add_trace(
            go.Bar(
                x=month_labels,
                y=diffs_by_type.get(transaction_type, [0.0] * len(month_labels)),
                name=transaction_type,
            )
        )

    fig.update_layout(
        title=f"Month-over-Month Change by Category (Last {month_count} Month{'s' if month_count != 1 else ''})",
        template="plotly_white",
        barmode="relative",
        bargap=0.28,
        barcornerradius=5,
        legend_title_text="Type",
        yaxis_title="Change vs Previous Month",
        xaxis_title="Month",
    )
    fig.add_hline(y=0, line_width=1, line_color="rgba(0, 0, 0, 0.35)")
    return fig


def create_month_vs_baseline_diff_figure(
    month_labels: list[str],
    types: list[str],
    diffs_by_type: dict[str, list[float]],
    baseline_month: str,
) -> go.Figure:
    fig = go.Figure()

    for transaction_type in types:
        fig.add_trace(
            go.Bar(
                x=month_labels,
                y=diffs_by_type.get(transaction_type, [0.0] * len(month_labels)),
                name=transaction_type,
            )
        )

    fig.update_layout(
        title=f"Change vs {baseline_month} by Category",
        template="plotly_white",
        barmode="relative",
        bargap=0.28,
        barcornerradius=5,
        legend_title_text="Type",
        yaxis_title=f"Change vs {baseline_month}",
        xaxis_title="Month",
    )
    fig.add_hline(y=0, line_width=1, line_color="rgba(0, 0, 0, 0.35)")
    return fig


def create_daily_month_comparison_figure(
    day_labels: list[int],
    month_labels: list[str],
    values_by_month: dict[str, list[float]],
    month_count: int,
) -> go.Figure:
    fig = go.Figure()

    for month_label in month_labels:
        fig.add_trace(
            go.Scatter(
                x=day_labels,
                y=values_by_month.get(month_label, [0.0] * len(day_labels)),
                mode="lines+markers",
                name=month_label,
                line={"shape": "spline", "smoothing": 0.3, "width": 2},
                marker={"size": 5},
            )
        )

    fig.update_layout(
        title=f"Daily Spend Comparison (Last {month_count} Month{'s' if month_count != 1 else ''})",
        template="plotly_white",
        legend_title_text="Month",
        xaxis_title="Day of Month",
        yaxis_title="Amount Spent",
        xaxis={"dtick": 1, "range": [0.5, 31.5]},
    )
    return fig
