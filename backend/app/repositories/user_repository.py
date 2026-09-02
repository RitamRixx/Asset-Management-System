"""User repository (data-access layer, section 42)."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.get(User, user_id)


def get_by_email(db: Session, email: str) -> Optional[User]:
    return db.scalar(select(User).where(User.email == email))


def get_by_employee_id(db: Session, employee_id: int) -> Optional[User]:
    return db.scalar(select(User).where(User.employee_id == employee_id))


def list_users(db: Session, skip: int = 0, limit: int = 50) -> list[User]:
    return list(db.scalars(select(User).offset(skip).limit(limit)))

def get_by_entra_identity(db: Session, entra_object_id: str, entra_tenant_id: str) -> Optional[User]:
    return db.scalar(
        select(User).where(
            User.entra_object_id == entra_object_id,
            User.entra_tenant_id == entra_tenant_id,
        )
    )


def create(db: Session, user: User) -> User:
    db.add(user)
    db.flush()
    return user
