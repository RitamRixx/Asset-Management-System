"""Repair ticket + history data-access layer (sections 25-26)."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import RepairStatus
from app.models.repair import RepairHistory, RepairTicket


def get_by_id(db: Session, ticket_id: int) -> Optional[RepairTicket]:
    return db.get(RepairTicket, ticket_id)


def list_tickets(
    db: Session,
    *,
    asset_id: Optional[int] = None,
    status_filter: Optional[RepairStatus] = None,
    skip: int = 0,
    limit: int = 50,
) -> list[RepairTicket]:
    stmt = select(RepairTicket)
    if asset_id is not None:
        stmt = stmt.where(RepairTicket.asset_id == asset_id)
    if status_filter is not None:
        stmt = stmt.where(RepairTicket.status == status_filter)
    stmt = stmt.offset(skip).limit(limit).order_by(RepairTicket.id.desc())
    return list(db.scalars(stmt))


def create_ticket(db: Session, ticket: RepairTicket) -> RepairTicket:
    db.add(ticket)
    db.flush()
    return ticket


def create_history_entry(db: Session, entry: RepairHistory) -> RepairHistory:
    db.add(entry)
    db.flush()
    return entry


def list_history(db: Session, ticket_id: int) -> list[RepairHistory]:
    stmt = (
        select(RepairHistory)
        .where(RepairHistory.repair_ticket_id == ticket_id)
        .order_by(RepairHistory.changed_at)
    )
    return list(db.scalars(stmt))
