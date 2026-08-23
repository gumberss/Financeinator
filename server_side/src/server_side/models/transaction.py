from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(slots=True, frozen=True)
class TransactionInsertion:
    date: date
    title: str
    amount: Decimal


@dataclass(slots=True, frozen=True)
class Transaction:
    id: int
    date: date
    title: str
    amount: Decimal
    type: str
