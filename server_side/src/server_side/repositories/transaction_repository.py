from server_side.models.transaction import Transaction, TransactionInsertion


class TransactionRepository:
    def __init__(self) -> None:
        self._next_id = 1

    def insert_many(
        self,
        transaction_insertions: list[TransactionInsertion],
        transaction_type: str,
    ) -> list[Transaction]:
        inserted_transactions: list[Transaction] = []

        for item in transaction_insertions:
            inserted_transactions.append(
                Transaction(
                    id=self._next_id,
                    date=item.date,
                    title=item.title,
                    amount=item.amount,
                    type=transaction_type,
                )
            )
            self._next_id += 1

        return inserted_transactions


transaction_repository = TransactionRepository()
