import random
import base64
from collections import defaultdict
from datetime import date
from decimal import Decimal

import requests
from dash import Dash, Input, Output, State, dash_table, dcc, html, no_update
from components import (
    create_bar_figure,
    create_daily_month_comparison_figure,
    create_donut_figure,
    create_line_figure,
    create_type_month_comparison_figure,
)


SERVER_IMPORT_URL = "http://127.0.0.1:8100/api/v1/transactions/import-csv"
SERVER_TRANSACTIONS_URL = "http://127.0.0.1:8100/api/v1/transactions/"
SERVER_TITLE_MAPPINGS_URL = "http://127.0.0.1:8100/api/v1/transactions/title-mappings"


def generate_sample_data() -> tuple[list[str], list[int], list[int]]:
    labels = [f"P{i}" for i in range(1, 13)]
    line_values = [random.randint(20, 100) for _ in labels]
    bar_values = [random.randint(10, 90) for _ in labels]
    return labels, line_values, bar_values


def import_transactions_csv(contents: str, filename: str | None) -> tuple[bool, str]:
    if not contents:
        return False, "Select a CSV file to upload."

    try:
        _, content_string = contents.split(",", maxsplit=1)
        csv_bytes = base64.b64decode(content_string)
    except ValueError:
        return False, "Invalid uploaded file format."

    file_name = filename or "transactions.csv"

    try:
        response = requests.post(
            SERVER_IMPORT_URL,
            files={"file": (file_name, csv_bytes, "text/csv")},
            timeout=15,
        )
    except requests.RequestException:
        return (
            False,
            "Could not reach the server. Start server_side API before importing.",
        )

    if response.ok:
        data = response.json()
        message = data.get("message") or "File accepted for import."
        return True, message

    detail = "Unknown import error"
    try:
        detail = response.json().get("detail", detail)
    except ValueError:
        detail = response.text or detail
    return False, f"Import failed: {detail}"


def monthly_expense_data() -> tuple[list[str], list[float], str | None]:
    transactions, error = fetch_transactions()
    if error is not None:
        return [], [], error

    by_month: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))

    for item in transactions:
        transaction_date = date.fromisoformat(item["date"])
        month_key = transaction_date.strftime("%Y-%m")
        by_month[month_key] += Decimal(str(item["amount"]))

    labels = sorted(by_month.keys())
    totals = [float(by_month[label]) for label in labels]
    return labels, totals, None


def fetch_transactions() -> tuple[list[dict], str | None]:
    try:
        response = requests.get(SERVER_TRANSACTIONS_URL, timeout=10)
        response.raise_for_status()
        transactions = response.json()
    except requests.RequestException:
        return [], "Could not load transactions from server."
    return transactions, None


def subtract_month(month: date) -> date:
    if month.month == 1:
        return date(month.year - 1, 12, 1)
    return date(month.year, month.month - 1, 1)


def last_n_month_labels(transactions: list[dict], count: int) -> list[str]:
    if transactions:
        most_recent = max(date.fromisoformat(t["date"]) for t in transactions)
        cursor = date(most_recent.year, most_recent.month, 1)
    else:
        today = date.today()
        cursor = date(today.year, today.month, 1)

    months: list[date] = []
    for _ in range(count):
        months.append(cursor)
        cursor = subtract_month(cursor)

    months.reverse()
    return [m.strftime("%Y-%m") for m in months]


def last_six_month_labels(transactions: list[dict]) -> list[str]:
    return last_n_month_labels(transactions, 6)


def month_window_label(month_count: int) -> str:
    return f"Last {month_count} Month{'s' if month_count != 1 else ''}"


def daily_month_spent_figure(transactions: list[dict], month_count: int) -> object:
    month_labels = last_n_month_labels(transactions, month_count)
    day_labels = list(range(1, 32))

    values_by_month: dict[str, list[float]] = {
        month_label: [0.0 for _ in day_labels] for month_label in month_labels
    }

    for item in transactions:
        transaction_date = date.fromisoformat(item["date"])
        month_key = transaction_date.strftime("%Y-%m")
        if month_key not in values_by_month:
            continue

        amount = Decimal(str(item.get("amount", 0)))
        spent_amount = float(amount if amount > 0 else Decimal("0"))
        values_by_month[month_key][transaction_date.day - 1] += spent_amount

    return create_daily_month_comparison_figure(day_labels, month_labels, values_by_month, month_count)


def top_spend_donut_figure(
    transactions: list[dict],
    group_key: str,
    top_count: int,
    title: str,
    month_count: int,
) -> object:
    month_labels = set(last_n_month_labels(transactions, month_count))
    totals_by_group: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))

    for item in transactions:
        transaction_date = date.fromisoformat(item["date"])
        if transaction_date.strftime("%Y-%m") not in month_labels:
            continue

        amount = Decimal(str(item.get("amount", 0)))
        if amount <= 0:
            continue

        group = str(item.get(group_key, "")).strip() or "Unmapped"
        totals_by_group[group] += amount

    ordered_totals = sorted(totals_by_group.items(), key=lambda item: item[1], reverse=True)
    top_totals = ordered_totals[:top_count]
    others_total = sum((total for _, total in ordered_totals[top_count:]), Decimal("0"))

    labels = [label for label, _ in top_totals]
    values = [float(total) for _, total in top_totals]

    if others_total > 0:
        labels.append("Others")
        values.append(float(others_total))

    return create_donut_figure(labels, values, title)


def invoice_items_by_category(
    transactions: list[dict],
    category: str | None,
    merchant: str | None = None,
    month_count: int = 6,
) -> list[dict[str, str]]:
    month_labels = set(last_n_month_labels(transactions, month_count))

    rows = [
        item
        for item in transactions
        if date.fromisoformat(item["date"]).strftime("%Y-%m") in month_labels
        and (category is None or str(item.get("type", "")).strip() == category)
        and (merchant is None or str(item.get("merchant", "")).strip() == merchant)
    ]
    rows.sort(key=lambda item: item["date"], reverse=True)

    return [
        {
            "date": item["date"],
            "title": item["title"],
            "amount": f"{Decimal(str(item.get('amount', 0))):.2f}",
            "type": str(item.get("type", "")).strip(),
            "merchant": str(item.get("merchant", "")).strip(),
        }
        for item in rows
    ]


def distinct_merchants(
    transactions: list[dict],
    category: str | None = None,
    month_count: int = 6,
) -> list[str]:
    month_labels = set(last_n_month_labels(transactions, month_count))

    return sorted(
        {
            str(item.get("merchant", "")).strip()
            for item in transactions
            if str(item.get("merchant", "")).strip()
            and date.fromisoformat(item["date"]).strftime("%Y-%m") in month_labels
            and (category is None or str(item.get("type", "")).strip() == category)
        }
    )


def type_month_spent_figure(
    transactions: list[dict],
    selected_types: list[str],
    month_count: int,
) -> tuple[object, list[str]]:
    month_labels = last_n_month_labels(transactions, month_count)
    available_types = sorted(
        {
            str(item.get("type", "")).strip()
            for item in transactions
            if str(item.get("type", "")).strip()
        }
    )

    active_types = [transaction_type for transaction_type in selected_types if transaction_type in available_types]
    if not active_types:
        active_types = available_types

    values_by_type: dict[str, list[float]] = {
        transaction_type: [0.0 for _ in month_labels]
        for transaction_type in active_types
    }

    month_index = {label: idx for idx, label in enumerate(month_labels)}
    for item in transactions:
        transaction_type = str(item.get("type", "")).strip()
        if transaction_type not in active_types:
            continue

        transaction_date = date.fromisoformat(item["date"])
        month_key = transaction_date.strftime("%Y-%m")
        if month_key not in month_index:
            continue

        amount = Decimal(str(item.get("amount", 0)))
        spent_amount = float(amount if amount > 0 else Decimal("0"))
        values_by_type[transaction_type][month_index[month_key]] += spent_amount

    figure = create_type_month_comparison_figure(month_labels, active_types, values_by_type, month_count)
    return figure, available_types


def fetch_title_mappings() -> tuple[list[dict[str, str]], str | None]:
    try:
        response = requests.get(SERVER_TITLE_MAPPINGS_URL, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return [], "Could not load title mappings from server."

    rows = response.json()
    normalized_rows = [
        {
            "title": str(item.get("title", "")).strip(),
            "type": str(item.get("type") or "").strip(),
            "merchant": str(item.get("merchant") or "").strip(),
        }
        for item in rows
    ]
    return normalized_rows, None


def submit_title_mappings(rows: list[dict[str, str]] | None) -> tuple[bool, str, list[dict[str, str]]]:
    if rows is None:
        return False, "No rows to save.", []

    payload = {
        "mappings": [
            {
                "title": str(row.get("title", "")).strip(),
                "type": str(row.get("type", "")).strip() or None,
                "merchant": str(row.get("merchant", "")).strip() or None,
            }
            for row in rows
            if str(row.get("title", "")).strip()
        ]
    }

    try:
        response = requests.post(SERVER_TITLE_MAPPINGS_URL, json=payload, timeout=12)
        response.raise_for_status()
    except requests.RequestException:
        return False, "Could not save mappings to server.", rows

    saved_rows = [
        {
            "title": str(item.get("title", "")).strip(),
            "type": str(item.get("type") or "").strip(),
            "merchant": str(item.get("merchant") or "").strip(),
        }
        for item in response.json()
    ]
    return True, "Type mappings saved.", saved_rows


def data_provision_layout() -> html.Div:
    mapping_rows, mapping_error = fetch_title_mappings()

    status_text = mapping_error or "Unmapped titles appear first. Fill the type and click Submit."
    status_color = "#9b1c1c" if mapping_error else "#2b4c7e"

    return html.Div(
        children=[
            html.H2("Data Provision"),
            html.P("Upload a CSV with columns: date,title,amount."),
            dcc.Upload(
                id="transaction-upload",
                children=html.Div("Drop CSV here or click to choose file"),
                multiple=False,
                style={
                    "width": "100%",
                    "height": "110px",
                    "lineHeight": "110px",
                    "borderWidth": "2px",
                    "borderStyle": "dashed",
                    "borderRadius": "14px",
                    "textAlign": "center",
                    "background": "#f8fbff",
                    "borderColor": "#9ebbe8",
                    "color": "#2b4c7e",
                    "fontWeight": "600",
                },
            ),
            html.Div(id="upload-result", style={"marginTop": "14px"}),
            html.Hr(style={"margin": "22px 0"}),
            html.H3("Transaction Title Type Mapping"),
            html.P(
                status_text,
                style={"marginBottom": "10px", "color": status_color, "fontWeight": "600"},
            ),
            dash_table.DataTable(
                id="title-mapping-table",
                columns=[
                    {"name": "Title", "id": "title", "editable": False},
                    {"name": "Type", "id": "type", "editable": True},
                    {"name": "Merchant", "id": "merchant", "editable": True},
                ],
                data=mapping_rows,
                editable=True,
                page_size=12,
                style_cell={
                    "padding": "8px",
                    "fontFamily": "Segoe UI",
                    "fontSize": "14px",
                    "textAlign": "left",
                },
                style_header={"fontWeight": "700", "backgroundColor": "#f2f7ff"},
                style_table={"border": "1px solid #d9e2f2", "borderRadius": "8px", "overflow": "hidden"},
            ),
            html.Button(
                "Submit Mapping",
                id="submit-title-mapping",
                n_clicks=0,
                style={
                    "marginTop": "12px",
                    "padding": "10px 14px",
                    "border": "1px solid #2b4c7e",
                    "borderRadius": "8px",
                    "background": "#2b4c7e",
                    "color": "#ffffff",
                    "fontWeight": "600",
                    "cursor": "pointer",
                },
            ),
            html.Div(id="title-mapping-result", style={"marginTop": "12px"}),
        ]
    )


def data_analysis_layout() -> html.Div:
    default_month_count = 6
    labels, monthly_totals, load_error = monthly_expense_data()
    transactions, transaction_error = fetch_transactions()
    default_type_figure, available_types = type_month_spent_figure(transactions, [], default_month_count)
    daily_month_figure = daily_month_spent_figure(transactions, default_month_count)
    top_merchants_figure = top_spend_donut_figure(
        transactions,
        group_key="merchant",
        top_count=10,
        title=f"Top 10 Merchants by Spend ({month_window_label(default_month_count)})",
        month_count=default_month_count,
    )
    top_categories_figure = top_spend_donut_figure(
        transactions,
        group_key="type",
        top_count=5,
        title=f"Top 5 Categories by Spend ({month_window_label(default_month_count)})",
        month_count=default_month_count,
    )
    default_category = available_types[0] if available_types else None
    available_merchants = distinct_merchants(transactions, default_category, default_month_count)

    if not labels:
        labels, line_values, bar_values = generate_sample_data()
        line_fig = create_line_figure(labels, line_values)
        bar_fig = create_bar_figure(labels, bar_values)
        message = load_error or "No transactions found yet. Showing sample data."
        alert = html.Div(
            message,
            style={
                "marginBottom": "10px",
                "padding": "10px 12px",
                "borderRadius": "10px",
                "border": "1px solid #b08900",
                "color": "#7a5d00",
                "background": "#fff9e6",
                "fontWeight": "600",
            },
        )
    else:
        line_fig = create_line_figure(labels, monthly_totals)
        bar_fig = create_bar_figure(labels, monthly_totals)
        alert = html.Div(
            "Monthly totals loaded from transactions.",
            style={
                "marginBottom": "10px",
                "padding": "10px 12px",
                "borderRadius": "10px",
                "border": "1px solid #1f7a3d",
                "color": "#1f7a3d",
                "background": "#eaf7ef",
                "fontWeight": "600",
            },
        )

    return html.Div(
        children=[
            html.H2("Data Analysis"),
            alert,
            html.Div(
                style={"marginBottom": "18px"},
                children=[
                    html.Label(
                        "Month range",
                        htmlFor="month-window",
                        style={"fontWeight": "700", "color": "#2b4c7e"},
                    ),
                    dcc.Slider(
                        id="month-window",
                        min=1,
                        max=6,
                        step=1,
                        value=default_month_count,
                        marks={month: str(month) for month in range(1, 7)},
                        tooltip={"placement": "bottom", "always_visible": False},
                    ),
                ],
            ),
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px"},
                children=[dcc.Graph(figure=line_fig), dcc.Graph(figure=bar_fig)],
            ),
            html.Hr(style={"margin": "22px 0"}),
            html.H3("Monthly Type Comparison"),
            html.P(
                transaction_error or "Select or unselect types to filter the comparison chart.",
                style={
                    "marginBottom": "10px",
                    "color": "#9b1c1c" if transaction_error else "#2b4c7e",
                    "fontWeight": "600",
                },
            ),
            dcc.Dropdown(
                id="type-filter",
                options=[{"label": transaction_type, "value": transaction_type} for transaction_type in available_types],
                value=available_types,
                multi=True,
                placeholder="Select transaction types",
                style={"marginBottom": "12px"},
            ),
            dcc.Graph(id="type-month-graph", figure=default_type_figure),
            html.Hr(style={"margin": "22px 0"}),
            html.H3("Daily Spend Comparison"),
            dcc.Graph(id="daily-month-graph", figure=daily_month_figure),
            html.Hr(style={"margin": "22px 0"}),
            html.H3("Top Spend Breakdown"),
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px"},
                children=[
                    dcc.Graph(id="top-merchants-graph", figure=top_merchants_figure),
                    dcc.Graph(id="top-categories-graph", figure=top_categories_figure),
                ],
            ),
            html.Hr(style={"margin": "22px 0"}),
            html.H3("Invoice Items by Category"),
            dcc.Dropdown(
                id="invoice-items-category-filter",
                options=[{"label": transaction_type, "value": transaction_type} for transaction_type in available_types],
                value=default_category,
                placeholder="Select a category",
                style={"marginBottom": "12px"},
            ),
            dcc.Dropdown(
                id="invoice-items-merchant-filter",
                options=[{"label": merchant, "value": merchant} for merchant in available_merchants],
                value=None,
                placeholder="Select a merchant (optional)",
                style={"marginBottom": "12px"},
            ),
            dash_table.DataTable(
                id="invoice-items-table",
                columns=[
                    {"name": "Date", "id": "date"},
                    {"name": "Title", "id": "title"},
                    {"name": "Amount", "id": "amount"},
                    {"name": "Type", "id": "type"},
                    {"name": "Merchant", "id": "merchant"},
                ],
                data=invoice_items_by_category(transactions, default_category, month_count=default_month_count),
                page_size=18,
                style_cell={
                    "padding": "8px",
                    "fontFamily": "Segoe UI",
                    "fontSize": "14px",
                    "textAlign": "left",
                },
                style_header={"fontWeight": "700", "backgroundColor": "#f2f7ff"},
                style_table={"border": "1px solid #d9e2f2", "borderRadius": "8px", "overflow": "hidden"},
            ),
        ]
    )


def create_app() -> Dash:
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div(
        style={"maxWidth": "1200px", "margin": "20px auto", "padding": "0 16px 24px"},
        children=[
            html.H1("Financeinator Client Dashboard"),
            dcc.Tabs(
                id="top-menu",
                value="data-provision",
                children=[
                    dcc.Tab(label="Data Provision", value="data-provision"),
                    dcc.Tab(label="Data Analysis", value="data-analysis"),
                ],
            ),
            html.Div(
                id="screen-content",
                style={"marginTop": "18px"},
            ),
        ],
    )

    @app.callback(Output("screen-content", "children"), Input("top-menu", "value"))
    def render_screen(active_screen: str) -> html.Div:
        if active_screen == "data-analysis":
            return data_analysis_layout()
        return data_provision_layout()

    @app.callback(
        Output("upload-result", "children"),
        Output("title-mapping-table", "data"),
        Input("transaction-upload", "contents"),
        State("transaction-upload", "filename"),
        prevent_initial_call=True,
    )
    def upload_csv(contents: str | None, filename: str | None) -> tuple[html.Div, list[dict[str, str]] | object]:
        if contents is None:
            return no_update, no_update

        success, message = import_transactions_csv(contents, filename)
        color = "#1f7a3d" if success else "#9b1c1c"
        background = "#eaf7ef" if success else "#fdecef"

        mapping_rows, _ = fetch_title_mappings()

        return (
            html.Div(
                message,
                style={
                    "padding": "10px 12px",
                    "borderRadius": "10px",
                    "border": f"1px solid {color}",
                    "color": color,
                    "background": background,
                    "fontWeight": "600",
                },
            ),
            mapping_rows,
        )

    @app.callback(
        Output("title-mapping-result", "children"),
        Output("title-mapping-table", "data", allow_duplicate=True),
        Input("submit-title-mapping", "n_clicks"),
        State("title-mapping-table", "data"),
        prevent_initial_call=True,
    )
    def submit_mapping(
        n_clicks: int,
        rows: list[dict[str, str]] | None,
    ) -> tuple[html.Div | object, list[dict[str, str]] | object]:
        if not n_clicks:
            return no_update, no_update

        success, message, saved_rows = submit_title_mappings(rows)
        color = "#1f7a3d" if success else "#9b1c1c"
        background = "#eaf7ef" if success else "#fdecef"

        return (
            html.Div(
                message,
                style={
                    "padding": "10px 12px",
                    "borderRadius": "10px",
                    "border": f"1px solid {color}",
                    "color": color,
                    "background": background,
                    "fontWeight": "600",
                },
            ),
            saved_rows if success else no_update,
        )

    @app.callback(
        Output("type-month-graph", "figure"),
        Input("type-filter", "value"),
        Input("month-window", "value"),
        prevent_initial_call=True,
    )
    def refresh_type_month_graph(selected_types: list[str] | None, month_count: int | None):
        transactions, _ = fetch_transactions()
        figure, _ = type_month_spent_figure(transactions, selected_types or [], month_count or 6)
        return figure

    @app.callback(
        Output("daily-month-graph", "figure"),
        Output("top-merchants-graph", "figure"),
        Output("top-categories-graph", "figure"),
        Input("month-window", "value"),
        prevent_initial_call=True,
    )
    def refresh_month_window_graphs(month_count: int | None):
        selected_month_count = month_count or 6
        transactions, _ = fetch_transactions()
        return (
            daily_month_spent_figure(transactions, selected_month_count),
            top_spend_donut_figure(
                transactions,
                group_key="merchant",
                top_count=10,
                title=f"Top 10 Merchants by Spend ({month_window_label(selected_month_count)})",
                month_count=selected_month_count,
            ),
            top_spend_donut_figure(
                transactions,
                group_key="type",
                top_count=5,
                title=f"Top 5 Categories by Spend ({month_window_label(selected_month_count)})",
                month_count=selected_month_count,
            ),
        )

    @app.callback(
        Output("invoice-items-merchant-filter", "options"),
        Output("invoice-items-merchant-filter", "value"),
        Input("invoice-items-category-filter", "value"),
        Input("month-window", "value"),
        State("invoice-items-merchant-filter", "value"),
        prevent_initial_call=True,
    )
    def refresh_invoice_items_merchant_options(
        selected_category: str | None,
        month_count: int | None,
        current_merchant: str | None,
    ):
        transactions, _ = fetch_transactions()
        merchants = distinct_merchants(transactions, selected_category, month_count or 6)
        options = [{"label": merchant, "value": merchant} for merchant in merchants]
        value = current_merchant if current_merchant in merchants else None
        return options, value

    @app.callback(
        Output("invoice-items-table", "data"),
        Input("invoice-items-category-filter", "value"),
        Input("invoice-items-merchant-filter", "value"),
        Input("month-window", "value"),
        prevent_initial_call=True,
    )
    def refresh_invoice_items_table(
        selected_category: str | None,
        selected_merchant: str | None,
        month_count: int | None,
    ):
        transactions, _ = fetch_transactions()
        return invoice_items_by_category(transactions, selected_category, selected_merchant, month_count or 6)

    return app


def run() -> None:
    app = create_app()
    app.run(host="127.0.0.1", port=8150, debug=False)


if __name__ == "__main__":
    run()
