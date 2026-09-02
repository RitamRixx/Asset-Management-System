"""Organization settings schemas (IAM Phase 8)."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class OrganizationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    company_name: str
    tagline: Optional[str]
    logo_url: Optional[str]
    email_notifications_default: bool
    updated_at: datetime


class OrganizationUpdate(BaseModel):
    company_name: Optional[str] = None
    tagline: Optional[str] = None
    logo_url: Optional[str] = None
    email_notifications_default: Optional[bool] = None