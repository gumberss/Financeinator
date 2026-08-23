class TitleTypeMappingRepository:
    def __init__(self) -> None:
        self._mappings: dict[str, str] = {}

    @staticmethod
    def _normalize_title(title: str) -> str:
        return title.strip().lower()

    def set_mapping(self, title: str, transaction_type: str) -> None:
        key = self._normalize_title(title)
        value = transaction_type.strip()

        if not key:
            return

        if value:
            self._mappings[key] = value
        elif key in self._mappings:
            del self._mappings[key]

    def set_many(self, mappings: list[tuple[str, str]]) -> None:
        for title, transaction_type in mappings:
            self.set_mapping(title, transaction_type)

    def get_mapping(self, title: str) -> str | None:
        return self._mappings.get(self._normalize_title(title))


title_type_mapping_repository = TitleTypeMappingRepository()
