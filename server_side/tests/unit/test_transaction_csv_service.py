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
