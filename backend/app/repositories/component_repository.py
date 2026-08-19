"""AssetComponent data-access layer."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.component import AssetComponent


def get_by_id(db: Session, component_id: int) -> Optional[AssetComponent]:
    return db.get(AssetComponent, component_id)


def list_for_asset(db: Session, asset_id: int) -> list[AssetComponent]:
    """Every component row for the asset, ACTIVE and REMOVED alike — this
    full list *is* the replacement history described in section 16."""
    stmt = (
        select(AssetComponent)
        .where(AssetComponent.asset_id == asset_id)
        .order_by(AssetComponent.installed_at)
    )
    return list(db.scalars(stmt))


def create(db: Session, component: AssetComponent) -> AssetComponent:
    db.add(component)
    db.flush()
    return component
