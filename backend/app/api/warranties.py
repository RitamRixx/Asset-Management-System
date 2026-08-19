"""Warranty router (section 27). Admin/IT manage; staff roles can read."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.database import get_db
from app.core.permissions import Role
from app.models.warranty import Warranty
from app.repositories import asset_repository, warranty_repository
from app.schemas.warranty import WarrantyCreate, WarrantyRead

router = APIRouter(tags=["warranties"])

STAFF_ROLES = (Role.ADMIN, Role.HR, Role.IT_SUPPORT)
MANAGE_ROLES = (Role.ADMIN, Role.IT_SUPPORT)


@router.post(
    "/warranties", response_model=WarrantyRead, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(*MANAGE_ROLES))],
)
def create_warranty(payload: WarrantyCreate, db: Session = Depends(get_db)) -> Warranty:
    if asset_repository.get_by_id(db, payload.asset_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset not found")
    warranty = Warranty(**payload.model_dump())
    warranty_repository.create(db, warranty)
    db.commit()
    db.refresh(warranty)
    return warranty


@router.get(
    "/assets/{asset_id}/warranties",
    response_model=list[WarrantyRead],
    dependencies=[Depends(require_role(*STAFF_ROLES))],
)
def list_asset_warranties(asset_id: int, db: Session = Depends(get_db)) -> list[Warranty]:
    return warranty_repository.list_for_asset(db, asset_id)


@router.get(
    "/warranties/expiring-soon",
    response_model=list[WarrantyRead],
    dependencies=[Depends(require_role(*STAFF_ROLES))],
)
def list_expiring_soon(within_days: int = 30, db: Session = Depends(get_db)) -> list[Warranty]:
    return warranty_repository.list_expiring_soon(db, within_days=within_days)


@router.get(
    "/warranties/expired",
    response_model=list[WarrantyRead],
    dependencies=[Depends(require_role(*STAFF_ROLES))],
)
def list_expired(db: Session = Depends(get_db)) -> list[Warranty]:
    return warranty_repository.list_expired(db)
