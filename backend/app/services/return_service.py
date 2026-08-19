"""
Return business logic (section 23 of the spec).

Maps return_condition -> asset status exactly as the spec's own diagram:
GOOD -> AVAILABLE, DAMAGED -> DAMAGED (IT opens a repair ticket separately,
Phase 12), MISSING -> LOST. Business rule #7: returning an asset always
closes its active assignment first — enforced here by requiring the item
be ACTIVE before anything is written.
"""
from datetime import datetime, timezone

from fastapi import HTTPException, status

from sqlalchemy.orm import Session

from app.models.assignment import AssignmentItem
from app.models.asset_return import AssetReturn
from app.models.enums import AssetStatus, AssignmentStatus, ReturnCondition
from app.repositories import asset_repository, transfer_repository
from app.services import audit_service

_CONDITION_TO_ASSET_STATUS = {
    ReturnCondition.GOOD: AssetStatus.AVAILABLE,
    ReturnCondition.DAMAGED: AssetStatus.DAMAGED,
    ReturnCondition.MISSING: AssetStatus.LOST,
}


def process_return(
    db: Session,
    *,
    item: AssignmentItem,
    return_condition: ReturnCondition,
    returned_by_employee_id: int | None,
    notes: str | None,
    actor_user_id: int,
) -> AssetReturn:
    if item.status != AssignmentStatus.ACTIVE:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "This assignment item is not currently active (already returned/transferred).",
        )

    now = datetime.now(timezone.utc)
    item.status = AssignmentStatus.RETURNED
    item.returned_at = now
    item.return_condition = return_condition
    db.flush()

    asset = asset_repository.get_by_id(db, item.asset_id)
    old_status = asset.status
    asset.status = _CONDITION_TO_ASSET_STATUS[return_condition]
    db.flush()

    asset_return = AssetReturn(
        assignment_item_id=item.id,
        returned_by_employee_id=returned_by_employee_id,
        received_by_user_id=actor_user_id,
        return_condition=return_condition,
        notes=notes,
    )
    transfer_repository.create_return(db, asset_return)

    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="ASSET_RETURNED",
        entity_type="Asset",
        entity_id=asset.id,
        old_value={"status": old_status.value, "assignment_item_status": "ACTIVE"},
        new_value={"status": asset.status.value, "return_condition": return_condition.value},
    )
    return asset_return
