from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class TransactionInsertion(BaseModel):
    date: date
    title: str
    amount: Decimal


class TransactionResponse(BaseModel):
    id: int
    date: date
    title: str
    amount: Decimal
    type: str
