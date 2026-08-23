import csv
import io
from datetime import date
from decimal import Decimal, InvalidOperation

from server_side.models.transaction import TransactionInsertion


class TransactionCsvError(ValueError):
    pass


def parse_transactions_csv(csv_text: str) -> list[TransactionInsertion]:
    transactions: list[TransactionInsertion] = []
    reader = csv.reader(io.StringIO(csv_text))

    for line_number, row in enumerate(reader, start=1):
        if not row or all(cell.strip() == "" for cell in row):
            continue

        if len(row) != 3:
            raise TransactionCsvError(
                f"Line {line_number}: expected 3 columns (date,title,amount)."
            )

        date_raw, title_raw, amount_raw = [cell.strip() for cell in row]

        if line_number == 1 and (date_raw, title_raw, amount_raw) == (
            "date",
            "title",
            "amount",
        ):
            continue

        if not title_raw:
            raise TransactionCsvError(f"Line {line_number}: title is required.")

        try:
            transaction_date = date.fromisoformat(date_raw)
        except ValueError as exc:
            raise TransactionCsvError(
                f"Line {line_number}: invalid date '{date_raw}', expected YYYY-MM-DD."
            ) from exc

        try:
            transaction_amount = Decimal(amount_raw)
        except InvalidOperation as exc:
            raise TransactionCsvError(
                f"Line {line_number}: invalid amount '{amount_raw}'."
            ) from exc

        transactions.append(
            TransactionInsertion(
                date=transaction_date,
                title=title_raw,
                amount=transaction_amount,
            )
        )

    return transactions
