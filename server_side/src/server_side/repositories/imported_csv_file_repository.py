import json
from datetime import datetime, timezone
from pathlib import Path

from server_side.models.imported_csv_file import ImportedCsvFile

_IMPORTED_CSV_FILES_FILE = Path(__file__).with_name("imported_csv_files.json")


class ImportedCsvFileRepository:
    def __init__(self, file_path: Path = _IMPORTED_CSV_FILES_FILE) -> None:
        self._next_id = 1
        self._files: list[ImportedCsvFile] = []
        self._hashes: set[str] = set()
        self._file_path = file_path
        self._loaded_from_file = False

    def _ensure_loaded(self) -> None:
        if self._loaded_from_file:
            return
        self._loaded_from_file = True

        if not self._file_path.exists():
            return

        try:
            entries = json.loads(self._file_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        for entry in entries:
            try:
                record = ImportedCsvFile(
                    id=int(entry["id"]),
                    file_hash=str(entry["file_hash"]),
                    imported_at=datetime.fromisoformat(str(entry["imported_at"])),
                )
            except (KeyError, TypeError, ValueError):
                continue

            self._files.append(record)
            self._hashes.add(record.file_hash)
            self._next_id = max(self._next_id, record.id + 1)

    def _save_to_file(self) -> None:
        entries = [
            {
                "id": record.id,
                "file_hash": record.file_hash,
                "imported_at": record.imported_at.isoformat(),
            }
            for record in self._files
        ]
        self._file_path.write_text(
            json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def exists(self, file_hash: str) -> bool:
        self._ensure_loaded()
        return file_hash in self._hashes

    def add(self, file_hash: str) -> ImportedCsvFile:
        self._ensure_loaded()
        record = ImportedCsvFile(
            id=self._next_id,
            file_hash=file_hash,
            imported_at=datetime.now(timezone.utc),
        )
        self._files.append(record)
        self._hashes.add(file_hash)
        self._next_id += 1
        self._save_to_file()
        return record

    def list_all(self) -> list[ImportedCsvFile]:
        self._ensure_loaded()
        return list(self._files)


imported_csv_file_repository = ImportedCsvFileRepository()
