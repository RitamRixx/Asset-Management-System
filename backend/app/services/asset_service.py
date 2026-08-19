"""
Asset business logic (section 14, business rules #1-3 and #10 of the spec).

The manual status-change endpoint intentionally cannot set ASSIGNED or
UNDER_REPAIR: those are exclusively side effects of the assignment service
(Phase 10) and repair service (Phase 12) respectively, keeping asset status
always transactionally consistent with the workflow that caused it (rule
#10) instead of letting two different code paths fight over one column.
"""
from typing import Any, Optional

from fastapi import HTTPException, status as http_status
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.enums import AssetStatus
from app.repositories import asset_repository
from app.services import audit_service
from app.utils.codes import reserve_id_and_code

# States a human (IT/Admin) may set directly via PATCH /assets/{id}/status.
# ASSIGNED and UNDER_REPAIR are excluded on purpose (see module docstring).
MANUALLY_SETTABLE_STATUSES = {
    AssetStatus.AVAILABLE,
    AssetStatus.RESERVED,
    AssetStatus.DAMAGED,
    AssetStatus.LOST,
    AssetStatus.RETIRED,
    AssetStatus.DISPOSED,
}


def create_asset(db: Session, data: dict[str, Any], actor_user_id: int) -> Asset:
    if data.get("serial_number"):
        existing = asset_repository.get_by_serial(db, data["serial_number"])
        if existing is not None:
            raise HTTPException(
                http_status.HTTP_409_CONFLICT,
                f"An asset with serial number {data['serial_number']} already exists",
            )

    next_id, code = reserve_id_and_code(db, table_name="assets", prefix="AST")
    asset = Asset(id=next_id, asset_code=code, status=AssetStatus.AVAILABLE, **data)
    asset_repository.create(db, asset)

    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="ASSET_CREATED",
        entity_type="Asset",
        entity_id=asset.id,
        new_value={"asset_code": asset.asset_code, "asset_type_id": asset.asset_type_id},
    )
    return asset


def update_asset(db: Session, asset: Asset, data: dict[str, Any], actor_user_id: int) -> Asset:
    if data.get("serial_number") and data["serial_number"] != asset.serial_number:
        existing = asset_repository.get_by_serial(db, data["serial_number"])
        if existing is not None and existing.id != asset.id:
            raise HTTPException(
                http_status.HTTP_409_CONFLICT,
                f"An asset with serial number {data['serial_number']} already exists",
            )

    old_value = {k: getattr(asset, k) for k in data.keys()}
    for key, value in data.items():
        setattr(asset, key, value)
    db.flush()

    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="ASSET_UPDATED",
        entity_type="Asset",
        entity_id=asset.id,
        old_value={k: str(v) for k, v in old_value.items()},
        new_value={k: str(v) for k, v in data.items()},
    )
    return asset


def change_status(
    db: Session, asset: Asset, new_status: AssetStatus, notes: Optional[str], actor_user_id: int
) -> Asset:
    if new_status not in MANUALLY_SETTABLE_STATUSES:
        raise HTTPException(
            http_status.HTTP_400_BAD_REQUEST,
            f"{new_status.value} can only be set via the assignment/repair workflow, "
            "not a direct status change.",
        )
    if asset.status == AssetStatus.ASSIGNED and new_status != AssetStatus.AVAILABLE:
        # Business rule #7: returning an asset must close its assignment first.
        raise HTTPException(
            http_status.HTTP_409_CONFLICT,
            "This asset is currently assigned. Process a return or transfer first.",
        )

    old_status = asset.status
    asset.status = new_status
    db.flush()

    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="ASSET_STATUS_CHANGED",
        entity_type="Asset",
        entity_id=asset.id,
        old_value={"status": old_status.value},
        new_value={"status": new_status.value, "notes": notes},
    )
    return asset


def assert_assignable(asset: Asset) -> None:
    """Business rules #1-3: LOST / RETIRED / UNDER_REPAIR assets can't be assigned."""
    if asset.status in Asset.NON_ASSIGNABLE_STATUSES:
        raise HTTPException(
            http_status.HTTP_409_CONFLICT,
            f"Asset {asset.asset_code} is {asset.status.value} and cannot be assigned.",
        )
    if asset.status == AssetStatus.ASSIGNED:
        raise HTTPException(
            http_status.HTTP_409_CONFLICT,
            f"Asset {asset.asset_code} is already assigned to someone else.",
        )
