"""Warranty schemas (section 27) — `computed_status` is derived, never stored."""
from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator


class WarrantyCreate(BaseModel):
    asset_id: int
    warranty_start: Optional[date] = None
    warranty_end: Optional[date] = None
    vendor_id: Optional[int] = None
    warranty_type: Optional[str] = None
    warranty_reference: Optional[str] = None


class WarrantyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    warranty_start: Optional[date]
    warranty_end: Optional[date]
    vendor_id: Optional[int]
    warranty_type: Optional[str]
    warranty_reference: Optional[str]
    computed_status: str = "UNKNOWN"

    @model_validator(mode="before")
    @classmethod
    def _include_computed_status(cls, obj):
        # `computed_status` is a Python @property on the ORM model, not a
        # column — from_attributes alone won't pick it up as a "before"
        # value automatically in every pydantic version, so it's pulled in
        # explicitly here.
        if isinstance(obj, dict):
            return obj
        data = {name: getattr(obj, name, None) for name in WarrantyRead.model_fields if name != "computed_status"}
        data["computed_status"] = getattr(obj, "computed_status", "UNKNOWN")
        return data
