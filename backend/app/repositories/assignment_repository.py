"""Assignment data-access layer (sections 19-21)."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.assignment import AssetAssignment, AssignmentItem
from app.models.enums import AssignmentStatus


def get_by_id(db: Session, assignment_id: int) -> Optional[AssetAssignment]:
    stmt = (
        select(AssetAssignment)
        .options(selectinload(AssetAssignment.items))
        .where(AssetAssignment.id == assignment_id)
    )
    return db.scalar(stmt)


def list_items(db: Session, assignment_id: int) -> list[AssignmentItem]:
    stmt = select(AssignmentItem).where(AssignmentItem.assignment_id == assignment_id)
    return list(db.scalars(stmt))


def list_for_employee(db: Session, employee_id: int) -> list[AssetAssignment]:
    stmt = (
        select(AssetAssignment)
        .where(AssetAssignment.employee_id == employee_id)
        .order_by(AssetAssignment.assigned_at.desc())
    )
    return list(db.scalars(stmt))


def get_active_item_for_asset(db: Session, asset_id: int) -> Optional[AssignmentItem]:
    """Answers "who currently holds asset X" (section 14's core question) —
    the latest AssignmentItem for this asset with status=ACTIVE."""
    stmt = (
        select(AssignmentItem)
        .where(AssignmentItem.asset_id == asset_id, AssignmentItem.status == AssignmentStatus.ACTIVE)
        .order_by(AssignmentItem.created_at.desc())
        .limit(1)
    )
    return db.scalar(stmt)


def get_item_by_id(db: Session, item_id: int) -> Optional[AssignmentItem]:
    return db.get(AssignmentItem, item_id)


def create_header(db: Session, assignment: AssetAssignment) -> AssetAssignment:
    db.add(assignment)
    db.flush()
    return assignment


def create_item(db: Session, item: AssignmentItem) -> AssignmentItem:
    db.add(item)
    db.flush()
    return item
