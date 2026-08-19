"""
Repair business logic (sections 25-26 of the spec).

On open: asset -> UNDER_REPAIR (blocks assignment per rule #3), and a
RepairHistory row records the None -> OPEN transition.

On resolve/close: asset goes back to ASSIGNED if it still has an active
AssignmentItem (the employee never physically lost custody, e.g. an
on-site repair) or AVAILABLE otherwise — mirroring section 25's "Asset
status: AVAILABLE or ASSIGNED" outcome exactly.
"""
from datetime import date
from typing import Optional

from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.enums import AssetStatus, RepairStatus
from app.models.repair import RepairHistory, RepairTicket
from app.repositories import assignment_repository, repair_repository, user_repository
from app.services import audit_service, notification_service
from app.utils.codes import reserve_id_and_code

TERMINAL_STATUSES = {RepairStatus.CLOSED, RepairStatus.CANCELLED}
RESOLVING_STATUSES = {RepairStatus.RESOLVED, RepairStatus.CLOSED}

# Statuses an asset must NOT already be in to accept a new repair ticket.
_BLOCKED_FOR_NEW_TICKET = {
    AssetStatus.UNDER_REPAIR,
    AssetStatus.RETIRED,
    AssetStatus.DISPOSED,
    AssetStatus.LOST,
}


def create_ticket(
    db: Session,
    *,
    asset: Asset,
    reported_by: int,
    issue: str,
    priority,
    actor_user_id: int,
) -> RepairTicket:
    if asset.status in _BLOCKED_FOR_NEW_TICKET:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"Asset {asset.asset_code} is {asset.status.value} and cannot have a new repair ticket opened.",
        )

    next_id, code = reserve_id_and_code(db, table_name="repair_tickets", prefix="RT")
    ticket = RepairTicket(
        id=next_id,
        ticket_code=code,
        asset_id=asset.id,
        reported_by=reported_by,
        issue=issue,
        priority=priority,
        status=RepairStatus.OPEN,
    )
    repair_repository.create_ticket(db, ticket)

    old_asset_status = asset.status
    asset.status = AssetStatus.UNDER_REPAIR
    db.flush()

    repair_repository.create_history_entry(
        db,
        RepairHistory(
            repair_ticket_id=ticket.id, from_status=None, to_status=RepairStatus.OPEN,
            changed_by=actor_user_id,
        ),
    )
    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="REPAIR_CREATED",
        entity_type="RepairTicket",
        entity_id=ticket.id,
        old_value={"asset_status": old_asset_status.value},
        new_value={"asset_status": asset.status.value, "ticket_code": ticket.ticket_code},
    )
    return ticket


def update_status(
    db: Session,
    *,
    ticket: RepairTicket,
    new_status: RepairStatus,
    diagnosis: Optional[str],
    vendor_id: Optional[int],
    repair_cost: Optional[Decimal],
    repair_start_date: Optional[date],
    repair_end_date: Optional[date],
    resolution: Optional[str],
    notes: Optional[str],
    actor_user_id: int,
) -> RepairTicket:
    if ticket.status in TERMINAL_STATUSES:
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"This ticket is already {ticket.status.value} and cannot be updated."
        )

    old_status = ticket.status
    ticket.status = new_status
    for field, value in (
        ("diagnosis", diagnosis),
        ("vendor_id", vendor_id),
        ("repair_cost", repair_cost),
        ("repair_start_date", repair_start_date),
        ("repair_end_date", repair_end_date),
        ("resolution", resolution),
    ):
        if value is not None:
            setattr(ticket, field, value)
    db.flush()

    repair_repository.create_history_entry(
        db,
        RepairHistory(
            repair_ticket_id=ticket.id, from_status=old_status, to_status=new_status,
            changed_by=actor_user_id, notes=notes,
        ),
    )

    if new_status in RESOLVING_STATUSES:
        from app.repositories import asset_repository

        asset = asset_repository.get_by_id(db, ticket.asset_id)
        active_item = assignment_repository.get_active_item_for_asset(db, asset.id)
        asset.status = AssetStatus.ASSIGNED if active_item is not None else AssetStatus.AVAILABLE
        db.flush()

    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="REPAIR_STATUS_CHANGED",
        entity_type="RepairTicket",
        entity_id=ticket.id,
        old_value={"status": old_status.value},
        new_value={"status": new_status.value},
    )

    if new_status in RESOLVING_STATUSES:
        reporter_user = user_repository.get_by_employee_id(db, ticket.reported_by)
        if reporter_user is not None:
            notification_service.notify(
                db,
                recipient_user_id=reporter_user.id,
                type="REPAIR_UPDATED",
                title="Repair request update",
                message=f"Your repair ticket {ticket.ticket_code} is now {new_status.value}.",
                related_entity_type="RepairTicket",
                related_entity_id=ticket.id,
            )

    return ticket
