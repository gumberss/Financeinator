import json
from pathlib import Path

_MAPPINGS_FILE = Path(__file__).with_name("mappings.json")


class TitleTypeMappingRepository:
    def __init__(self) -> None:
        self._mappings: dict[str, str] = {}
        self._merchants: dict[str, str] = {}
        self._original_titles: dict[str, str] = {}
        self._loaded_from_file = False

    def _ensure_loaded(self) -> None:
        if self._loaded_from_file:
            return
        self._loaded_from_file = True

        if not _MAPPINGS_FILE.exists():
            return

        try:
            entries = json.loads(_MAPPINGS_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        for entry in entries:
            title = str(entry.get("title", ""))
            transaction_type = entry.get("type") or ""
            merchant = entry.get("merchant") or ""
            self._apply_mapping(title, transaction_type)
            self._apply_merchant(title, merchant)

    def _apply_mapping(self, title: str, transaction_type: str) -> None:
        key = self._normalize_title(title)
        value = transaction_type.strip()

        if not key:
            return

        self._original_titles.setdefault(key, title.strip())

        if value:
            self._mappings[key] = value
        elif key in self._mappings:
            del self._mappings[key]

    def _apply_merchant(self, title: str, merchant: str) -> None:
        key = self._normalize_title(title)
        value = merchant.strip()

        if not key:
            return

        self._original_titles.setdefault(key, title.strip())

        if value:
            self._merchants[key] = value
        elif key in self._merchants:
            del self._merchants[key]

    def _save_to_file(self) -> None:
        entries = [
            {
                "title": self._original_titles[key],
                "type": self._mappings.get(key),
                "merchant": self._merchants.get(key),
            }
            for key in self._original_titles
        ]
        _MAPPINGS_FILE.write_text(
            json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    @staticmethod
    def _normalize_title(title: str) -> str:
        return title.strip().lower()

    def set_mapping(self, title: str, transaction_type: str) -> None:
        self._ensure_loaded()
        self._apply_mapping(title, transaction_type)
        self._save_to_file()

    def set_many(self, mappings: list[tuple[str, str]]) -> None:
        self._ensure_loaded()
        for title, transaction_type in mappings:
            self._apply_mapping(title, transaction_type)
        self._save_to_file()

    def set_merchant(self, title: str, merchant: str) -> None:
        self._ensure_loaded()
        self._apply_merchant(title, merchant)
        self._save_to_file()

    def set_many_merchants(self, merchants: list[tuple[str, str]]) -> None:
        self._ensure_loaded()
        for title, merchant in merchants:
            self._apply_merchant(title, merchant)
        self._save_to_file()

    def get_mapping(self, title: str) -> str | None:
        self._ensure_loaded()
        return self._mappings.get(self._normalize_title(title))

    def get_merchant(self, title: str) -> str | None:
        self._ensure_loaded()
        return self._merchants.get(self._normalize_title(title))

    def list_distinct_categories(self) -> list[str]:
        self._ensure_loaded()
        return sorted({category for category in self._mappings.values()})

    def list_distinct_merchants(self) -> list[str]:
        self._ensure_loaded()
        return sorted({merchant for merchant in self._merchants.values()})


title_type_mapping_repository = TitleTypeMappingRepository()


