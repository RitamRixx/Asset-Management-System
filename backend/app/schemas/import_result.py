"""Bulk CSV import result schemas."""
from pydantic import BaseModel


class ImportRowError(BaseModel):
    row: int
    message: str


class ImportResult(BaseModel):
    created: int
    skipped: int
    errors: list[ImportRowError]
