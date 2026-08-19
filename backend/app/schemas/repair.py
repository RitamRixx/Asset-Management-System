"""Repair ticket schemas (sections 25-26)."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import RepairPriority, RepairStatus


class RepairTicketCreate(BaseModel):
    asset_id: int
    reported_by: int
    issue: str
    priority: RepairPriority = RepairPriority.MEDIUM


class RepairStatusUpdate(BaseModel):
    status: RepairStatus
    diagnosis: Optional[str] = None
    vendor_id: Optional[int] = None
    repair_cost: Optional[Decimal] = None
    repair_start_date: Optional[date] = None
    repair_end_date: Optional[date] = None
    resolution: Optional[str] = None
    notes: Optional[str] = None


class RepairTicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_code: str
    asset_id: int
    reported_by: int
    issue: str
    priority: RepairPriority
    status: RepairStatus
    diagnosis: Optional[str]
    vendor_id: Optional[int]
    repair_cost: Optional[Decimal]
    repair_start_date: Optional[date]
    repair_end_date: Optional[date]
    resolution: Optional[str]
    created_at: datetime


class RepairHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    repair_ticket_id: int
    from_status: Optional[RepairStatus]
    to_status: RepairStatus
    changed_by: Optional[int]
    changed_at: datetime
    notes: Optional[str]
