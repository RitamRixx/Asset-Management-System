"""Asset data-access layer (section 14, plus the filters listed in section 28)."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.enums import AssetStatus


def get_by_id(db: Session, asset_id: int) -> Optional[Asset]:
    return db.get(Asset, asset_id)


def get_by_code(db: Session, asset_code: str) -> Optional[Asset]:
    return db.scalar(select(Asset).where(Asset.asset_code == asset_code))


def get_by_serial(db: Session, serial_number: str) -> Optional[Asset]:
    return db.scalar(select(Asset).where(Asset.serial_number == serial_number))


def list_assets(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 50,
    asset_type_id: Optional[int] = None,
    location_id: Optional[int] = None,
    org_unit_id: Optional[int] = None,
    status_filter: Optional[AssetStatus] = None,
    manufacturer: Optional[str] = None,
    model: Optional[str] = None,
    vendor_id: Optional[int] = None,
    q: Optional[str] = None,
) -> list[Asset]:
    stmt = select(Asset)
    if asset_type_id is not None:
        stmt = stmt.where(Asset.asset_type_id == asset_type_id)
    if location_id is not None:
        stmt = stmt.where(Asset.location_id == location_id)
    if org_unit_id is not None:
        stmt = stmt.where(Asset.org_unit_id == org_unit_id)
    if status_filter is not None:
        stmt = stmt.where(Asset.status == status_filter)
    if manufacturer is not None:
        stmt = stmt.where(Asset.manufacturer.ilike(f"%{manufacturer}%"))
    if model is not None:
        stmt = stmt.where(Asset.model.ilike(f"%{model}%"))
    if vendor_id is not None:
        stmt = stmt.where(Asset.vendor_id == vendor_id)
    if q:
        # Global-search-style match (section 35): asset code, serial, hostname, model.
        pattern = f"%{q}%"
        stmt = stmt.where(
            Asset.asset_code.ilike(pattern)
            | Asset.serial_number.ilike(pattern)
            | Asset.hostname.ilike(pattern)
            | Asset.model.ilike(pattern)
        )
    stmt = stmt.offset(skip).limit(limit).order_by(Asset.id)
    return list(db.scalars(stmt))


def count_by_status(db: Session) -> dict[str, int]:
    """Powers the inventory dashboard's status breakdown (section 28)."""
    from sqlalchemy import func

    rows = db.execute(
        select(Asset.status, func.count(Asset.id)).group_by(Asset.status)
    ).all()
    return {status.value: count for status, count in rows}


def create(db: Session, asset: Asset) -> Asset:
    db.add(asset)
    db.flush()
    return asset
