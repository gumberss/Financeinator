from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class ImportedCsvFile:
    id: int
    file_hash: str
    imported_at: datetime
