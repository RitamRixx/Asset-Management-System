"""
Groups router (IAM Phase 6).

Follows the same lookup-table pattern as reference.py: Admin manages,
any staff role can list (needed to populate the employee-edit dropdown).
Deliberately no PATCH/DELETE yet — same reasoning as Department: groups
aren't hard-deleted once employees may reference them; retiring one is
future work if it's ever needed, not a gap in this phase.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.database import get_db
from app.core.permissions import Role
from app.models.group import Group
from app.schemas.group import GroupCreate, GroupRead

router = APIRouter(prefix="/groups", tags=["groups"])

STAFF_ROLES = (Role.ADMIN, Role.HR, Role.IT_SUPPORT)


@router.post(
    "", response_model=GroupRead, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def create_group(payload: GroupCreate, db: Session = Depends(get_db)) -> Group:
    group = Group(**payload.model_dump())
    db.add(group)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, f"'{payload.name}' already exists.")
    db.refresh(group)
    return group


@router.get("", response_model=list[GroupRead], dependencies=[Depends(require_role(*STAFF_ROLES))])
def list_groups(db: Session = Depends(get_db)) -> list[Group]:
    from app.repositories import group_repository
    return group_repository.list_groups(db)