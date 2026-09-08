import json

from server_side.repositories.imported_csv_file_repository import ImportedCsvFileRepository


def test_add_persists_imported_csv_file_hash_to_json(tmp_path) -> None:
    file_path = tmp_path / "imported_csv_files.json"
    repository = ImportedCsvFileRepository(file_path=file_path)

    repository.add("abc123")

    entries = json.loads(file_path.read_text(encoding="utf-8"))

    assert entries[0]["id"] == 1
    assert entries[0]["file_hash"] == "abc123"
    assert "imported_at" in entries[0]


def test_repository_loads_existing_imported_csv_file_hashes(tmp_path) -> None:
    file_path = tmp_path / "imported_csv_files.json"
    file_path.write_text(
        json.dumps(
            [
                {
                    "id": 3,
                    "file_hash": "abc123",
                    "imported_at": "2026-08-07T12:30:00+00:00",
                }
            ]
        ),
        encoding="utf-8",
    )
    repository = ImportedCsvFileRepository(file_path=file_path)

    assert repository.exists("abc123")
    assert repository.add("def456").id == 4