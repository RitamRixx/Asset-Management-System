"""
Assignment business logic (sections 19-21, business rules #1-4, #10).

`create_assignment` is the "BEGIN TRANSACTION ... COMMIT" example from
section 40 made real: header + every item + every asset's status flip all
happen against the same session and only reach the DB together, via the
API layer's single `db.commit()` after this function returns. If any asset
fails the assignability check, an exception propagates, nothing commits,
and the caller sees a clean 409 — never a half-created assignment.
"""
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.assignment import AssetAssignment, AssignmentItem
from app.models.enums import AssetStatus, AssignmentStatus
from app.repositories import asset_repository, assignment_repository, user_repository
from app.services import asset_service, audit_service, notification_service


def create_assignment(db: Session, data: dict[str, Any], actor_user_id: int) -> AssetAssignment:
    item_inputs = data.pop("items")

    # Validate every asset up front, before writing anything (rules #1-3).
    assets = []
    for item_input in item_inputs:
        asset = asset_repository.get_by_id(db, item_input["asset_id"])
        if asset is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, f"Asset {item_input['asset_id']} not found"
            )
        asset_service.assert_assignable(asset)
        assets.append(asset)

    assignment = AssetAssignment(assigned_by=actor_user_id, **data)
    assignment_repository.create_header(db, assignment)

    for item_input, asset in zip(item_inputs, assets):
        item = AssignmentItem(
            assignment_id=assignment.id,
            asset_id=asset.id,
            condition_at_assignment=item_input.get("condition_at_assignment") or asset.condition,
            status=AssignmentStatus.ACTIVE,
        )
        assignment_repository.create_item(db, item)

        asset.status = AssetStatus.ASSIGNED
        db.flush()

        audit_service.log_action(
            db,
            actor_user_id=actor_user_id,
            action="ASSET_ASSIGNED",
            entity_type="Asset",
            entity_id=asset.id,
            new_value={"employee_id": assignment.employee_id, "assignment_id": assignment.id},
        )

    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="ASSIGNMENT_CREATED",
        entity_type="AssetAssignment",
        entity_id=assignment.id,
        new_value={"employee_id": assignment.employee_id, "item_count": len(item_inputs)},
    )

    recipient = user_repository.get_by_employee_id(db, assignment.employee_id)
    if recipient is not None:
        notification_service.notify(
            db,
            recipient_user_id=recipient.id,
            type="ASSET_ASSIGNED",
            title="New asset handover",
            message=f"You've been assigned {len(item_inputs)} asset(s). Please review and acknowledge.",
            related_entity_type="AssetAssignment",
            related_entity_id=assignment.id,
        )

    return assignment


def acknowledge_assignment(
    db: Session, assignment: AssetAssignment, actor_user_id: int
) -> AssetAssignment:
    if assignment.acknowledged_at is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "This handover was already acknowledged.")

    assignment.acknowledged_at = datetime.now(timezone.utc)
    db.flush()

    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="ASSIGNMENT_ACKNOWLEDGED",
        entity_type="AssetAssignment",
        entity_id=assignment.id,
    )
    return assignment
