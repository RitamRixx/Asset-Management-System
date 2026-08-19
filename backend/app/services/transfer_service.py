"""
Transfer business logic (section 22 of the spec, business rule #8).

Only IT/Admin can call the transfer endpoint (RBAC), so the request and
approval happen in the same step here rather than a separate pending
queue — but the *history* still looks exactly like the spec's diagram:
the old AssignmentItem is closed with status=TRANSFERRED (distinct from
RETURNED, so reports can tell "handed back" apart from "handed to someone
else"), and a brand-new AssetAssignment/AssignmentItem is opened for the
destination employee. Nothing is overwritten — rule #8.
"""
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.assignment import AssetAssignment, AssignmentItem
from app.models.asset import Asset
from app.models.enums import AssignmentStatus, TransferStatus
from app.models.transfer import AssetTransfer
from app.repositories import assignment_repository, transfer_repository
from app.services import audit_service


def transfer_asset(
    db: Session,
    *,
    asset: Asset,
    to_employee_id: int,
    notes: str | None,
    actor_user_id: int,
) -> AssetTransfer:
    current_item = assignment_repository.get_active_item_for_asset(db, asset.id)
    if current_item is None:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"Asset {asset.asset_code} is not currently assigned to anyone, so it can't be "
            "transferred (use the assignment workflow instead).",
        )

    from_employee_id = current_item.assignment.employee_id
    if from_employee_id == to_employee_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Asset is already assigned to this employee.")

    now = datetime.now(timezone.utc)

    # Close the old side.
    current_item.status = AssignmentStatus.TRANSFERRED
    current_item.returned_at = now
    db.flush()

    # Open the new side (fresh handover transaction, per section 21's model).
    new_assignment = AssetAssignment(
        employee_id=to_employee_id,
        assigned_by=actor_user_id,
        notes=notes or f"Transferred from employee {from_employee_id}",
    )
    assignment_repository.create_header(db, new_assignment)
    new_item = AssignmentItem(
        assignment_id=new_assignment.id,
        asset_id=asset.id,
        condition_at_assignment=asset.condition,
        status=AssignmentStatus.ACTIVE,
    )
    assignment_repository.create_item(db, new_item)

    transfer = AssetTransfer(
        asset_id=asset.id,
        from_employee_id=from_employee_id,
        to_employee_id=to_employee_id,
        requested_by=actor_user_id,
        approved_by=actor_user_id,
        status=TransferStatus.COMPLETED,
        completed_at=now,
        notes=notes,
    )
    transfer_repository.create_transfer(db, transfer)

    # Asset stays ASSIGNED throughout — just to someone new — so no status
    # write needed here (unlike a return, which frees the asset up).

    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="ASSET_TRANSFERRED",
        entity_type="Asset",
        entity_id=asset.id,
        old_value={"employee_id": from_employee_id},
        new_value={"employee_id": to_employee_id, "transfer_id": transfer.id},
    )
    return transfer
