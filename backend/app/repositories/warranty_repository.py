"""Warranty data-access layer (section 27)."""
from datetime import date, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.warranty import EXPIRING_SOON_WINDOW_DAYS, Warranty


def get_by_id(db: Session, warranty_id: int) -> Optional[Warranty]:
    return db.get(Warranty, warranty_id)


def list_for_asset(db: Session, asset_id: int) -> list[Warranty]:
    stmt = select(Warranty).where(Warranty.asset_id == asset_id).order_by(Warranty.warranty_end.desc())
    return list(db.scalars(stmt))


def list_expiring_soon(db: Session, within_days: int = EXPIRING_SOON_WINDOW_DAYS) -> list[Warranty]:
    today = date.today()
    stmt = select(Warranty).where(
        Warranty.warranty_end.is_not(None),
        Warranty.warranty_end >= today,
        Warranty.warranty_end <= today + timedelta(days=within_days),
    )
    return list(db.scalars(stmt))


def list_expired(db: Session) -> list[Warranty]:
    stmt = select(Warranty).where(Warranty.warranty_end.is_not(None), Warranty.warranty_end < date.today())
    return list(db.scalars(stmt))


def create(db: Session, warranty: Warranty) -> Warranty:
    db.add(warranty)
    db.flush()
    return warranty
