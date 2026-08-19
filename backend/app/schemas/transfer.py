"""Return + Transfer schemas (sections 22-23)."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import ReturnCondition, TransferStatus


class AssetReturnCreate(BaseModel):
    assignment_item_id: int
    return_condition: ReturnCondition
    returned_by_employee_id: Optional[int] = None
    notes: Optional[str] = None


class AssetReturnRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    assignment_item_id: int
    returned_by_employee_id: Optional[int]
    received_by_user_id: int
    return_condition: ReturnCondition
    returned_at: datetime
    notes: Optional[str]


class TransferCreate(BaseModel):
    asset_id: int
    to_employee_id: int
    notes: Optional[str] = None


class TransferRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    from_employee_id: int
    to_employee_id: int
    requested_by: Optional[int]
    approved_by: Optional[int]
    status: TransferStatus
    requested_at: datetime
    completed_at: Optional[datetime]
    notes: Optional[str]
