from server_side.models.transaction import Transaction, TransactionInsertion
from server_side.repositories.title_type_mapping_repository import (
    title_type_mapping_repository,
)


class TransactionRepository:
    def __init__(self) -> None:
        self._next_id = 1
        self._transactions: list[Transaction] = []

    def insert_many(
        self,
        transaction_insertions: list[TransactionInsertion],
        transaction_type: str,
    ) -> list[Transaction]:
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

        return inserted_transactions

    def list_all(self) -> list[Transaction]:
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
