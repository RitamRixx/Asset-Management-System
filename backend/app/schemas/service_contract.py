"""
Service Contract schemas (Phase C).
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ServiceContractCreate(BaseModel):
    vendor_id: Optional[int] = None
    contract_number: Optional[str] = None
    start_date: date
    end_date: date
    cost: Optional[Decimal] = None
    notes: Optional[str] = None


class ServiceContractUpdate(BaseModel):
    vendor_id: Optional[int] = None
    contract_number: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    cost: Optional[Decimal] = None
    notes: Optional[str] = None


class ServiceContractRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    vendor_id: Optional[int]
    contract_number: Optional[str]
    start_date: date
    end_date: date
    cost: Optional[Decimal]
    notes: Optional[str]
    created_at: datetime
