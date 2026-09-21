"""OrgUnit business logic (Phase A)."""
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.org import OrgUnit
from app.repositories import org_unit_repository
from app.services import audit_service


def create_org_unit(
    db: Session,
    *,
    name: str,
    unit_type_id: int,
    code: Optional[str] = None,
    parent_id: Optional[int] = None,
    address: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    country: Optional[str] = None,
    manager_id: Optional[int] = None,
    actor_user_id: int,
) -> OrgUnit:
    
    if parent_id is not None:
        parent = org_unit_repository.get(db, parent_id)
        if not parent:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Parent OrgUnit not found.")

    unit = OrgUnit(
        name=name,
        code=code,
        unit_type_id=unit_type_id,
        parent_id=parent_id,
        address=address,
        city=city,
        state=state,
        country=country,
        manager_id=manager_id,
        status="ACTIVE",
    )
    
    org_unit_repository.create(db, unit)

    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="ORG_UNIT_CREATED",
        entity_type="OrgUnit",
        entity_id=unit.id,
        new_value={"name": name, "unit_type_id": unit_type_id, "parent_id": parent_id},
    )
    
    return unit


def update_org_unit_status(
    db: Session,
    *,
    org_unit_id: int,
    new_status: str,
    actor_user_id: int,
) -> OrgUnit:
    """Soft delete / disable pattern."""
    unit = org_unit_repository.get(db, org_unit_id)
    if not unit:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "OrgUnit not found.")

    old_status = unit.status
    if old_status == new_status:
        return unit

    unit.status = new_status
    org_unit_repository.update(db, unit)

    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="ORG_UNIT_STATUS_CHANGED",
        entity_type="OrgUnit",
        entity_id=unit.id,
        old_value={"status": old_status},
        new_value={"status": new_status},
    )
    return unit
