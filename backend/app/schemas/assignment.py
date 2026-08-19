"""Assignment schemas (sections 19-21)."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AssetCondition, AssignmentStatus, ReturnCondition


class AssignmentItemCreate(BaseModel):
    asset_id: int
    condition_at_assignment: Optional[AssetCondition] = None


class AssignmentCreate(BaseModel):
    employee_id: int
    expected_return_date: Optional[datetime] = None
    notes: Optional[str] = None
    items: list[AssignmentItemCreate] = Field(min_length=1)


class AssignmentItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    assignment_id: int
    asset_id: int
    condition_at_assignment: Optional[AssetCondition]
    status: AssignmentStatus
    returned_at: Optional[datetime]
    return_condition: Optional[ReturnCondition]
    notes: Optional[str]


class AssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    assigned_by: int
    assigned_at: datetime
    expected_return_date: Optional[datetime]
    acknowledged_at: Optional[datetime]
    notes: Optional[str]
    items: list[AssignmentItemRead] = []


class CurrentAssignmentRead(BaseModel):
    """Answers section 30's "Assignment: Current Employee, Assigned Date"
    for the asset detail page — derived from the active AssignmentItem
    rather than a stored column, per models/assignment.py's design."""

    assignment_item_id: int
    assignment_id: int
    asset_id: int
    employee_id: int
    assigned_at: datetime
