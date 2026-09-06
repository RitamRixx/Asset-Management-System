"""
Self-service user account actions (IAM Phase 9).

Separate from users.py's Admin-driven create/list/disable — this module
is specifically the "acting on your own account" surface, so it never
takes a target user_id, only the authenticated current_user.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.enums import AuthProvider
from app.models.user import User
from app.services import audit_service, token_service


def change_password(
    db: Session, *, user: User, current_password: str, new_password: str
) -> None:
    if user.auth_provider != AuthProvider.LOCAL or user.password_hash is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "This account signs in with Microsoft and has no AMS-managed password to change.",
        )
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Current password is incorrect.")

    user.password_hash = hash_password(new_password)
    db.flush()

    audit_service.log_action(
        db, actor_user_id=user.id, action="PASSWORD_CHANGED", entity_type="User", entity_id=user.id,
    )

    # Revoke every other outstanding session — the one making this
    # request will get a fresh token from a subsequent login as normal;
    # this doesn't revoke the token being used *right now* to make this
    # call (see api/users.py — that'd log the caller out mid-request).
    token_service.revoke_all_for_user(db, user.id)