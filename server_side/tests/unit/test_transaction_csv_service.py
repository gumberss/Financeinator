from decimal import Decimal

import pytest

from server_side.services.transaction_csv_service import (
    TransactionCsvError,
    parse_transactions_csv,
)


def test_parse_transactions_csv_returns_transaction_insertions() -> None:
    csv_text = "2026-08-01,Coffee,12.50\n2026-08-02,Book,35.00\n"

    transactions = parse_transactions_csv(csv_text)

    assert len(transactions) == 2
    assert transactions[0].title == "Coffee"
    assert transactions[0].amount == Decimal("12.50")


def test_parse_transactions_csv_invalid_amount_raises_error() -> None:
    csv_text = "2026-08-01,Coffee,abc\n"

    with pytest.raises(TransactionCsvError):
        parse_transactions_csv(csv_text)


def test_parse_transactions_csv_accepts_comma_decimal_template() -> None:
    csv_text = (
        "date,title,amount\n"
        "2026-08-23,Mlp*Estante V-Sebo Liv,\"34,74\"\n"
        "2026-08-23,99app *99app,\"8,19\"\n"
        "2026-08-23,Dl*Uberrides,\"5,45\"\n"
    )

    transactions = parse_transactions_csv(csv_text)

    assert len(transactions) == 3
    assert transactions[0].amount == Decimal("34.74")
    assert transactions[1].amount == Decimal("8.19")
    assert transactions[2].amount == Decimal("5.45")
