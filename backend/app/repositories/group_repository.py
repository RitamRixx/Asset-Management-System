"""Group data-access layer (IAM Phase 6)."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.group import Group


def get_by_id(db: Session, group_id: int) -> Optional[Group]:
    return db.get(Group, group_id)


def list_groups(db: Session) -> list[Group]:
    return list(db.scalars(select(Group).order_by(Group.name)))


def create(db: Session, group: Group) -> Group:
    db.add(group)
    db.flush()
    return group