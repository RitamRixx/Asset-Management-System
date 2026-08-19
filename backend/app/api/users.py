"""
User management router (Phase 4/5).

Only Admins can create, list, or disable accounts (section 4). Any
authenticated user can read their own `/users/me`.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.core.permissions import Role
from app.core.security import hash_password
from app.models.enums import UserStatus
from app.models.user import User
from app.repositories import user_repository
from app.schemas.user import UserCreate, UserRead, UserStatusUpdate
from app.services import audit_service

router = APIRouter()


@router.get("/users/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post(
    "/users",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    if user_repository.get_by_email(db, payload.email) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "A user with this email already exists")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        employee_id=payload.employee_id,
    )
    user_repository.create(db, user)
    audit_service.log_action(
        db,
        actor_user_id=current_user.id,
        action="USER_CREATED",
        entity_type="User",
        entity_id=user.id,
        new_value={"email": user.email, "role": user.role.value},
    )
    db.commit()
    db.refresh(user)
    return user


@router.get(
    "/users",
    response_model=list[UserRead],
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def list_users(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)) -> list[User]:
    return user_repository.list_users(db, skip=skip, limit=limit)


@router.patch(
    "/users/{user_id}/status",
    response_model=UserRead,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    old_status = user.status
    user.status = payload.status
    audit_service.log_action(
        db,
        actor_user_id=current_user.id,
        action="USER_DISABLED" if payload.status == UserStatus.DISABLED else "USER_ENABLED",
        entity_type="User",
        entity_id=user.id,
        old_value={"status": old_status.value},
        new_value={"status": user.status.value},
    )
    db.commit()
    db.refresh(user)
    return user
