from datetime import date
from decimal import Decimal

from server_side.models.transaction import TransactionInsertion
from server_side.repositories.title_type_mapping_repository import (
    title_type_mapping_repository,
)
from server_side.repositories.transaction_repository import TransactionRepository


def test_insert_many_persists_transactions_in_memory() -> None:
    repository = TransactionRepository()

    inserted = repository.insert_many(
        [
            TransactionInsertion(date=date(2026, 8, 1), title="Coffee", amount=Decimal("5.90")),
            TransactionInsertion(date=date(2026, 8, 2), title="Book", amount=Decimal("32.10")),
        ],
        transaction_type="purchase",
    )

    stored = repository.list_all()

    assert len(inserted) == 2
    assert len(stored) == 2
    assert stored[0].id == 1
    assert stored[1].id == 2
    assert stored[0].type == "purchase"


def test_insert_many_marks_pagamento_recebido_as_card_payment() -> None:
    repository = TransactionRepository()

    inserted = repository.insert_many(
        [
            TransactionInsertion(
                date=date(2026, 8, 7),
                title="Pagamento recebido",
                amount=Decimal("-2508.70"),
            )
        ],
        transaction_type="purchase",
    )

    assert len(inserted) == 1
    assert inserted[0].type == "card payment"


def test_insert_many_uses_title_type_mapping() -> None:
    repository = TransactionRepository()
    title_type_mapping_repository.set_mapping("Coffee", "food")

    inserted = repository.insert_many(
        [
            TransactionInsertion(
                date=date(2026, 8, 7),
                title="Coffee",
                amount=Decimal("10.50"),
            )
        ],
        transaction_type="purchase",
    )

    assert inserted[0].type == "food"
    title_type_mapping_repository.set_mapping("Coffee", "")
