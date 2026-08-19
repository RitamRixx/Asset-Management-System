"""
Component business logic (sections 15-16 of the spec).

`replace_component` is the one that matters: it never does
`component.description = new_value`. Instead — old component removed,
new component added, both linked — exactly the workflow section 16 spells
out, so a full timeline is always reconstructable from `list_for_asset`.
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.component import AssetComponent
from app.models.enums import ComponentStatus
from app.repositories import component_repository
from app.services import audit_service


def install_component(
    db: Session,
    *,
    asset_id: int,
    component_type_id: int,
    description: str,
    serial_number: Optional[str],
    actor_user_id: int,
) -> AssetComponent:
    component = AssetComponent(
        asset_id=asset_id,
        component_type_id=component_type_id,
        description=description,
        serial_number=serial_number,
        status=ComponentStatus.ACTIVE,
    )
    component_repository.create(db, component)

    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="COMPONENT_INSTALLED",
        entity_type="AssetComponent",
        entity_id=component.id,
        new_value={"asset_id": asset_id, "description": description},
    )
    return component


def replace_component(
    db: Session,
    *,
    old_component: AssetComponent,
    new_description: str,
    new_serial_number: Optional[str],
    actor_user_id: int,
) -> AssetComponent:
    if old_component.status != ComponentStatus.ACTIVE:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "This component has already been removed/replaced and cannot be replaced again.",
        )

    new_component = AssetComponent(
        asset_id=old_component.asset_id,
        component_type_id=old_component.component_type_id,
        description=new_description,
        serial_number=new_serial_number,
        status=ComponentStatus.ACTIVE,
    )
    component_repository.create(db, new_component)  # flush -> gets an id

    old_component.status = ComponentStatus.REMOVED
    old_component.removed_at = datetime.now(timezone.utc)
    old_component.replaced_by_component_id = new_component.id
    db.flush()

    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="COMPONENT_REPLACED",
        entity_type="AssetComponent",
        entity_id=old_component.asset_id,
        old_value={"old_component_id": old_component.id, "description": old_component.description},
        new_value={"new_component_id": new_component.id, "description": new_description},
    )
    return new_component
