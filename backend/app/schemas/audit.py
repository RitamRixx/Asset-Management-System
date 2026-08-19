"""Audit log read schema (section 31)."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_user_id: Optional[int]
    action: str
    entity_type: str
    entity_id: Optional[int]
    old_value: Optional[dict]
    new_value: Optional[dict]
    timestamp: datetime
    ip_address: Optional[str]
