"""
Asset schemas (section 14 of the spec).

`AssetUpdate` deliberately excludes `status`: ASSIGNED is only ever set by
the assignment service (Phase 10) and UNDER_REPAIR only by the repair
service (Phase 12). Manual status changes (damaged/lost/retired/disposed/
available/reserved) go through `AssetStatusChange` + the dedicated
`/assets/{id}/status` endpoint, which enforces which transitions are
allowed manually (see services/asset_service.py).
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import AssetCondition, AssetStatus


class AssetCreate(BaseModel):
    asset_type_id: int
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_cost: Optional[Decimal] = None
    vendor_id: Optional[int] = None
    condition: AssetCondition = AssetCondition.NEW
    location_id: Optional[int] = None
    org_unit_id: Optional[int] = None
    hostname: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    salvage_value: Optional[Decimal] = None
    useful_life_years: Optional[int] = None


class AssetUpdate(BaseModel):
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    vendor_id: Optional[str] = None
    condition: Optional[AssetCondition] = None
    location_id: Optional[int] = None
    org_unit_id: Optional[int] = None
    hostname: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    salvage_value: Optional[Decimal] = None
    useful_life_years: Optional[int] = None


class AssetStatusChange(BaseModel):
    status: AssetStatus
    notes: Optional[str] = None


class AssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_code: str
    asset_type_id: int
    manufacturer: Optional[str]
    model: Optional[str]
    serial_number: Optional[str]
    purchase_date: Optional[date]
    purchase_cost: Optional[Decimal]
    vendor_id: Optional[int]
    status: AssetStatus
    condition: AssetCondition
    location_id: Optional[int]
    org_unit_id: Optional[int]
    hostname: Optional[str]
    description: Optional[str]
    tags: list[str]
    salvage_value: Optional[Decimal]
    useful_life_years: Optional[int]
    depreciated_value: Optional[Decimal]
    created_at: datetime
