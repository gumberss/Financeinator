from fastapi import APIRouter, File, HTTPException, UploadFile

from server_side.repositories.imported_csv_file_repository import (
    imported_csv_file_repository,
)
from server_side.repositories.transaction_repository import transaction_repository
from server_side.repositories.title_type_mapping_repository import (
    title_type_mapping_repository,
)
from server_side.schemas.title_mapping import (
    TitleTypeMappingItem,
    TitleTypeMappingUpdateRequest,
)
from server_side.schemas.transaction import TransactionResponse
from server_side.services.transaction_csv_service import (
    TransactionCsvError,
    hash_csv_content,
    parse_transactions_csv,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _is_visible_to_client(transaction_type: str) -> bool:
    return transaction_type != "card payment"


def _effective_type(transaction) -> str:
    mapped_type = title_type_mapping_repository.get_mapping(transaction.title)
    if mapped_type and mapped_type.strip():
        return mapped_type.strip()
    return transaction.type


def _to_response(transaction) -> TransactionResponse:
    effective_type = _effective_type(transaction)
    return TransactionResponse(
        id=transaction.id,
        date=transaction.date,
        title=transaction.title,
        amount=transaction.amount,
        type=effective_type,
    )


@router.get("/title-mappings", response_model=list[TitleTypeMappingItem])
def list_title_mappings() -> list[TitleTypeMappingItem]:
    distinct_titles = sorted({t.title.strip() for t in transaction_repository.list_all() if t.title.strip()})

    rows = [
        TitleTypeMappingItem(
            title=title,
            type=title_type_mapping_repository.get_mapping(title),
        )
        for title in distinct_titles
    ]

    rows.sort(key=lambda item: (item.type is not None and item.type.strip() != "", item.title.lower()))
    return rows


@router.post("/title-mappings", response_model=list[TitleTypeMappingItem])
def save_title_mappings(payload: TitleTypeMappingUpdateRequest) -> list[TitleTypeMappingItem]:
    title_type_mapping_repository.set_many(
        [(item.title, item.type or "") for item in payload.mappings]
    )
    return list_title_mappings()


@router.get("/", response_model=list[TransactionResponse])
def list_transactions() -> list[TransactionResponse]:
    transactions = [
        t
        for t in transaction_repository.list_all()
        if _is_visible_to_client(_effective_type(t))
    ]
    return [
        _to_response(t)
        for t in transactions
    ]


@router.post("/import-csv", response_model=list[TransactionResponse])
async def import_transactions_csv(file: UploadFile = File(...)) -> list[TransactionResponse]:
    raw_bytes = await file.read()
    file_hash = hash_csv_content(raw_bytes)

    if imported_csv_file_repository.exists(file_hash):
        raise HTTPException(status_code=409, detail="This CSV file has already been imported.")

    try:
        csv_text = raw_bytes.decode("utf-8-sig")
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
    imported_csv_file_repository.add(file_hash)

    visible_transactions = [
        t for t in transactions if _is_visible_to_client(_effective_type(t))
    ]

    return [
        _to_response(t)
        for t in visible_transactions
    ]
