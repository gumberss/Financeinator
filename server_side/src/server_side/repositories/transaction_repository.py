import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from server_side.models.transaction import Transaction, TransactionInsertion
from server_side.repositories.title_type_mapping_repository import (
    title_type_mapping_repository,
)

_TRANSACTIONS_FILE = Path(__file__).with_name("transactions.json")


class TransactionRepository:
    def __init__(self, file_path: Path = _TRANSACTIONS_FILE) -> None:
        self._next_id = 1
        self._transactions: list[Transaction] = []
        self._file_path = file_path
        self._loaded_from_file = False

    def _ensure_loaded(self) -> None:
        if self._loaded_from_file:
            return
        self._loaded_from_file = True

        if not self._file_path.exists():
            return

        try:
            entries = json.loads(self._file_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        for entry in entries:
            try:
                transaction = Transaction(
                    id=int(entry["id"]),
                    date=date.fromisoformat(str(entry["date"])),
                    title=str(entry["title"]),
                    amount=Decimal(str(entry["amount"])),
                    type=str(entry["type"]),
                )
            except (KeyError, TypeError, ValueError):
                continue

            self._transactions.append(transaction)
            self._next_id = max(self._next_id, transaction.id + 1)

    def _save_to_file(self) -> None:
        entries = [
            {
                "id": transaction.id,
                "date": transaction.date.isoformat(),
                "title": transaction.title,
                "amount": str(transaction.amount),
                "type": transaction.type,
            }
            for transaction in self._transactions
        ]
        self._file_path.write_text(
            json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def insert_many(
        self,
        transaction_insertions: list[TransactionInsertion],
        transaction_type: str,
    ) -> list[Transaction]:
        self._ensure_loaded()
        inserted_transactions: list[Transaction] = []

        for item in transaction_insertions:
            resolved_type = self._resolve_transaction_type(item.title, transaction_type)
            transaction = Transaction(
                id=self._next_id,
                date=item.date,
                title=item.title,
                amount=item.amount,
                type=resolved_type,
            )
            inserted_transactions.append(transaction)
            self._transactions.append(transaction)
            self._next_id += 1

        self._save_to_file()
        return inserted_transactions

    def list_all(self) -> list[Transaction]:
        self._ensure_loaded()
        return list(self._transactions)

    @staticmethod
    def _resolve_transaction_type(title: str, default_type: str) -> str:
        mapped_type = title_type_mapping_repository.get_mapping(title)
        if mapped_type:
            return mapped_type

        if title.strip().lower() == "pagamento recebido":
            return "card payment"
        return default_type


transaction_repository = TransactionRepository()
