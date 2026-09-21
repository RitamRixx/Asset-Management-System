"""
Asset Disposal service logic (Phase C).
"""
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.asset_disposal import AssetDisposal
from app.models.enums import AssetStatus
from app.services import audit_service


def dispose_asset(
    db: Session, asset: Asset, data: dict[str, Any], actor_user_id: int
) -> AssetDisposal:
    if asset.status == AssetStatus.ASSIGNED:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Cannot dispose an asset that is currently assigned. Process a return first.",
        )
    if asset.status == AssetStatus.DISPOSED:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "This asset is already disposed.",
        )

    disposal = AssetDisposal(
        asset_id=asset.id,
        authorized_by_id=actor_user_id,
        **data,
    )
    db.add(disposal)

    old_status = asset.status
    asset.status = AssetStatus.DISPOSED
    db.flush()

    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="ASSET_DISPOSED",
        entity_type="Asset",
        entity_id=asset.id,
        old_value={"status": old_status.value},
        new_value={
            "status": AssetStatus.DISPOSED.value,
            "disposal_method": data.get("disposal_method"),
            "disposal_value": str(data.get("disposal_value")) if data.get("disposal_value") else None,
            "notes": data.get("notes"),
        },
    )
    
    return disposal
