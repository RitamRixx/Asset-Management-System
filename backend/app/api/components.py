"""Components router (sections 15-16). Install/replace restricted to IT/Admin."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.core.permissions import Role
from app.models.component import AssetComponent
from app.models.user import User
from app.repositories import asset_repository, component_repository
from app.schemas.component import ComponentInstall, ComponentRead, ComponentReplace
from app.services import component_service

router = APIRouter(tags=["components"])

STAFF_ROLES = (Role.ADMIN, Role.HR, Role.IT_SUPPORT)
MANAGE_ROLES = (Role.ADMIN, Role.IT_SUPPORT)


@router.get(
    "/assets/{asset_id}/components",
    response_model=list[ComponentRead],
    dependencies=[Depends(require_role(*STAFF_ROLES))],
)
def list_components(asset_id: int, db: Session = Depends(get_db)) -> list[AssetComponent]:
    if asset_repository.get_by_id(db, asset_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset not found")
    return component_repository.list_for_asset(db, asset_id)


@router.post(
    "/assets/{asset_id}/components",
    response_model=ComponentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(*MANAGE_ROLES))],
)
def install_component(
    asset_id: int,
    payload: ComponentInstall,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssetComponent:
    if asset_repository.get_by_id(db, asset_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset not found")

    component = component_service.install_component(
        db,
        asset_id=asset_id,
        component_type_id=payload.component_type_id,
        description=payload.description,
        serial_number=payload.serial_number,
        actor_user_id=current_user.id,
    )
    db.commit()
    db.refresh(component)
    return component


@router.post(
    "/components/{component_id}/replace",
    response_model=ComponentRead,
    dependencies=[Depends(require_role(*MANAGE_ROLES))],
)
def replace_component(
    component_id: int,
    payload: ComponentReplace,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssetComponent:
    old_component = component_repository.get_by_id(db, component_id)
    if old_component is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Component not found")

    new_component = component_service.replace_component(
        db,
        old_component=old_component,
        new_description=payload.description,
        new_serial_number=payload.serial_number,
        actor_user_id=current_user.id,
    )
    db.commit()
    db.refresh(new_component)
    return new_component
