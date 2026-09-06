from datetime import datetime, timezone

from server_side.models.imported_csv_file import ImportedCsvFile


class ImportedCsvFileRepository:
    def __init__(self) -> None:
        self._next_id = 1
        self._files: list[ImportedCsvFile] = []
        self._hashes: set[str] = set()

    def exists(self, file_hash: str) -> bool:
        return file_hash in self._hashes

    def add(self, file_hash: str) -> ImportedCsvFile:
        record = ImportedCsvFile(
            id=self._next_id,
            file_hash=file_hash,
            imported_at=datetime.now(timezone.utc),
        )
        self._files.append(record)
        self._hashes.add(file_hash)
        self._next_id += 1
        return record

    def list_all(self) -> list[ImportedCsvFile]:
        return list(self._files)


imported_csv_file_repository = ImportedCsvFileRepository()
