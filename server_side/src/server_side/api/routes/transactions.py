from fastapi import APIRouter, File, HTTPException, UploadFile

from server_side.repositories.transaction_repository import transaction_repository
from server_side.schemas.transaction import TransactionResponse
from server_side.services.transaction_csv_service import (
    TransactionCsvError,
    parse_transactions_csv,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/import-csv", response_model=list[TransactionResponse])
async def import_transactions_csv(file: UploadFile = File(...)) -> list[TransactionResponse]:
    try:
        csv_text = (await file.read()).decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded.") from exc

    try:
        transaction_insertions = parse_transactions_csv(csv_text)
    except TransactionCsvError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    transactions = transaction_repository.insert_many(
        transaction_insertions,
        transaction_type="purchase",
    )

    return [
        TransactionResponse(
            id=t.id,
            date=t.date,
            title=t.title,
            amount=t.amount,
            type=t.type,
        )
        for t in transactions
    ]
