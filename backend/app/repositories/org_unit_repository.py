"""OrgUnit repository (Phase A)."""
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from app.models.org import OrgUnit, OrgUnitType


def get(db: Session, org_unit_id: int) -> Optional[OrgUnit]:
    return db.get(OrgUnit, org_unit_id)


def get_by_name(db: Session, name: str) -> Optional[OrgUnit]:
    return db.scalar(select(OrgUnit).where(OrgUnit.name == name))


def get_all(db: Session) -> Sequence[OrgUnit]:
    return db.scalars(select(OrgUnit).order_by(OrgUnit.name)).all()


def create(db: Session, obj: OrgUnit) -> OrgUnit:
    db.add(obj)
    db.flush()
    return obj


def update(db: Session, obj: OrgUnit) -> OrgUnit:
    db.flush()
    return obj


def get_subtree(db: Session, root_id: int) -> Sequence[OrgUnit]:
    """
    Returns all descendants of the given root_id, including the root itself.
    Uses a recursive CTE to traverse the parent_id hierarchy downwards.
    """
    cte = select(OrgUnit).where(OrgUnit.id == root_id).cte(name="subtree_cte", recursive=True)
    
    parent_alias = select(OrgUnit).where(OrgUnit.parent_id == cte.c.id)
    cte = cte.union_all(parent_alias)

    return db.scalars(select(OrgUnit).join(cte, OrgUnit.id == cte.c.id)).all()


def get_ancestors(db: Session, leaf_id: int) -> Sequence[OrgUnit]:
    """
    Returns all ancestors of the given leaf_id, including the leaf itself.
    Uses a recursive CTE to traverse the parent_id hierarchy upwards.
    """
    cte = select(OrgUnit).where(OrgUnit.id == leaf_id).cte(name="ancestor_cte", recursive=True)
    
    parent_alias = select(OrgUnit).where(OrgUnit.id == cte.c.parent_id)
    cte = cte.union_all(parent_alias)

    return db.scalars(select(OrgUnit).join(cte, OrgUnit.id == cte.c.id)).all()


def get_types(db: Session) -> Sequence[OrgUnitType]:
    return db.scalars(select(OrgUnitType).order_by(OrgUnitType.typical_rank)).all()


def get_type(db: Session, type_id: int) -> Optional[OrgUnitType]:
    return db.get(OrgUnitType, type_id)


def create_type(db: Session, obj: OrgUnitType) -> OrgUnitType:
    db.add(obj)
    db.flush()
    return obj
