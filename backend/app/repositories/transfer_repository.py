"""Return + Transfer data-access layer (sections 22-23)."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset_return import AssetReturn
from app.models.transfer import AssetTransfer


def create_return(db: Session, ret: AssetReturn) -> AssetReturn:
    db.add(ret)
    db.flush()
    return ret


def list_returns_for_asset(db: Session, asset_id: int) -> list[AssetReturn]:
    # Joins through assignment_items to filter by asset — kept in the
    # service/repository boundary rather than a raw join here since it's
    # only used by the (light) reporting layer later.
    from app.models.assignment import AssignmentItem

    stmt = (
        select(AssetReturn)
        .join(AssignmentItem, AssetReturn.assignment_item_id == AssignmentItem.id)
        .where(AssignmentItem.asset_id == asset_id)
        .order_by(AssetReturn.returned_at.desc())
    )
    return list(db.scalars(stmt))


def create_transfer(db: Session, transfer: AssetTransfer) -> AssetTransfer:
    db.add(transfer)
    db.flush()
    return transfer


def get_transfer(db: Session, transfer_id: int) -> Optional[AssetTransfer]:
    return db.get(AssetTransfer, transfer_id)


def list_transfers_for_asset(db: Session, asset_id: int) -> list[AssetTransfer]:
    stmt = (
        select(AssetTransfer)
        .where(AssetTransfer.asset_id == asset_id)
        .order_by(AssetTransfer.requested_at.desc())
    )
    return list(db.scalars(stmt))
