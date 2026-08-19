"""Returns + Transfers router (sections 22-23). IT/Admin only."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.core.permissions import Role
from app.models.asset_return import AssetReturn
from app.models.transfer import AssetTransfer
from app.models.user import User
from app.repositories import asset_repository, assignment_repository, transfer_repository
from app.schemas.transfer import (
    AssetReturnCreate,
    AssetReturnRead,
    TransferCreate,
    TransferRead,
)
from app.services import return_service, transfer_service

router = APIRouter(tags=["returns-transfers"])

MANAGE_ROLES = (Role.ADMIN, Role.IT_SUPPORT)


@router.post(
    "/returns", response_model=AssetReturnRead, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(*MANAGE_ROLES))],
)
def create_return(
    payload: AssetReturnCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssetReturn:
    item = assignment_repository.get_item_by_id(db, payload.assignment_item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Assignment item not found")

    asset_return = return_service.process_return(
        db,
        item=item,
        return_condition=payload.return_condition,
        returned_by_employee_id=payload.returned_by_employee_id,
        notes=payload.notes,
        actor_user_id=current_user.id,
    )
    db.commit()
    db.refresh(asset_return)
    return asset_return


@router.get(
    "/assets/{asset_id}/returns",
    response_model=list[AssetReturnRead],
    dependencies=[Depends(require_role(*MANAGE_ROLES))],
)
def list_asset_returns(asset_id: int, db: Session = Depends(get_db)) -> list[AssetReturn]:
    return transfer_repository.list_returns_for_asset(db, asset_id)


@router.post(
    "/transfers", response_model=TransferRead, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(*MANAGE_ROLES))],
)
def create_transfer(
    payload: TransferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssetTransfer:
    asset = asset_repository.get_by_id(db, payload.asset_id)
    if asset is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset not found")

    transfer = transfer_service.transfer_asset(
        db,
        asset=asset,
        to_employee_id=payload.to_employee_id,
        notes=payload.notes,
        actor_user_id=current_user.id,
    )
    db.commit()
    db.refresh(transfer)
    return transfer


@router.get(
    "/assets/{asset_id}/transfers",
    response_model=list[TransferRead],
    dependencies=[Depends(require_role(*MANAGE_ROLES))],
)
def list_asset_transfers(asset_id: int, db: Session = Depends(get_db)) -> list[AssetTransfer]:
    return transfer_repository.list_transfers_for_asset(db, asset_id)
