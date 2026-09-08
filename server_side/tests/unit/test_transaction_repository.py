from datetime import date
from decimal import Decimal
import json

from server_side.models.transaction import TransactionInsertion
from server_side.repositories.title_type_mapping_repository import (
    title_type_mapping_repository,
)
from server_side.repositories.transaction_repository import TransactionRepository


def test_insert_many_persists_transactions_in_memory(tmp_path) -> None:
    repository = TransactionRepository(file_path=tmp_path / "transactions.json")

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


def test_insert_many_marks_pagamento_recebido_as_card_payment(tmp_path) -> None:
    repository = TransactionRepository(file_path=tmp_path / "transactions.json")

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


def test_insert_many_uses_title_type_mapping(monkeypatch, tmp_path) -> None:
    repository = TransactionRepository(file_path=tmp_path / "transactions.json")
    monkeypatch.setattr(
        title_type_mapping_repository,
        "get_mapping",
        lambda title: "food" if title == "Coffee" else None,
    )

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


def test_insert_many_persists_transactions_to_json(tmp_path) -> None:
    file_path = tmp_path / "transactions.json"
    repository = TransactionRepository(file_path=file_path)

    repository.insert_many(
        [
            TransactionInsertion(
                date=date(2026, 8, 7),
                title="Coffee",
                amount=Decimal("10.50"),
            )
        ],
        transaction_type="purchase",
    )

    entries = json.loads(file_path.read_text(encoding="utf-8"))

    assert entries == [
        {
            "id": 1,
            "date": "2026-08-07",
            "title": "Coffee",
            "amount": "10.50",
            "type": "purchase",
        }
    ]


def test_repository_loads_existing_transactions_json(tmp_path) -> None:
    file_path = tmp_path / "transactions.json"
    file_path.write_text(
        json.dumps(
            [
                {
                    "id": 7,
                    "date": "2026-08-07",
                    "title": "Coffee",
                    "amount": "10.50",
                    "type": "purchase",
                }
            ]
        ),
        encoding="utf-8",
    )
    repository = TransactionRepository(file_path=file_path)

    inserted = repository.insert_many(
        [
            TransactionInsertion(
                date=date(2026, 8, 8),
                title="Book",
                amount=Decimal("32.10"),
            )
        ],
        transaction_type="purchase",
    )

    assert inserted[0].id == 8
    assert len(repository.list_all()) == 2
