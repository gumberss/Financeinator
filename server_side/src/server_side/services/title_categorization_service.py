from server_side.clients.llm.item_categorization_service import categorize_item
from server_side.clients.llm.merchant_identification_service import identify_merchant
from server_side.models.transaction import TransactionInsertion
from server_side.repositories.title_type_mapping_repository import (
    title_type_mapping_repository,
)

_SKIPPED_TITLES = {"pagamento recebido"}


def ensure_title_mappings(transaction_insertions: list[TransactionInsertion]) -> None:
    distinct_titles = list(
        dict.fromkeys(
            item.title.strip() for item in transaction_insertions if item.title.strip()
        )
    )

    for title in distinct_titles:
        if title.lower() in _SKIPPED_TITLES:
            continue

        if title_type_mapping_repository.get_mapping(title) is None:
            categories = title_type_mapping_repository.list_distinct_categories()
            category = categorize_item(title, categories)
            title_type_mapping_repository.set_mapping(title, category)

        if title_type_mapping_repository.get_merchant(title) is None:
            merchants = title_type_mapping_repository.list_distinct_merchants()
            merchant = identify_merchant(title, merchants)
            title_type_mapping_repository.set_merchant(title, merchant)

