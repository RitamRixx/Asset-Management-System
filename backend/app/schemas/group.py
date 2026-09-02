"""Group schemas (IAM Phase 2 model, CRUD wired up in Phase 6)."""
from typing import Optional

from pydantic import BaseModel, ConfigDict


class GroupCreate(BaseModel):
    name: str
    code: Optional[str] = None


class GroupRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    code: Optional[str]
    status: str