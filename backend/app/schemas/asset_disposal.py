"""
Asset Disposal schemas (Phase C).
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import DisposalMethod


class AssetDisposalCreate(BaseModel):
    disposal_date: date
    disposal_method: DisposalMethod
    disposal_value: Optional[Decimal] = None
    notes: Optional[str] = None


class AssetDisposalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    disposal_date: date
    disposal_method: DisposalMethod
    disposal_value: Optional[Decimal]
    authorized_by_id: int
    notes: Optional[str]
    created_at: datetime
