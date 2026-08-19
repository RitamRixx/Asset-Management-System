"""Notification schemas (section 33)."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    title: str
    message: str
    related_entity_type: Optional[str]
    related_entity_id: Optional[int]
    is_read: bool
    created_at: datetime
