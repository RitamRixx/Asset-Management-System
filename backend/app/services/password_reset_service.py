"""
Password reset business logic (IAM Phase 4).

Mirrors the DeviceAgent / SSO-state token pattern already in this codebase
— only a SHA-256 hash of the raw token is ever stored. `request_password_reset`
always no-ops silently for unknown emails or MICROSOFT-provider accounts,
so this endpoint can't be used to enumerate registered users.
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models.password_reset import PasswordResetToken
from app.models.user import User
from app.repositories import password_reset_repository, user_repository
from app.services import audit_service, email_service


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()


def request_password_reset(db: Session, email: str) -> None:
    user = user_repository.get_by_email(db, email)
    if user is None or user.password_hash is None:
        return  # unknown email, or SSO-only account — silent no-op

    raw_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
    )
    token = PasswordResetToken(
        user_id=user.id, token_hash=_hash_token(raw_token), expires_at=expires_at
    )
    password_reset_repository.create(db, token)

    reset_link = f"{settings.FRONTEND_BASE_URL}/reset-password?token={raw_token}"
    email_service.send_email(
        to=user.email,
        subject="Reset your AMS Platform password",
        body=f"Use this link within {settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes:\n\n{reset_link}",
    )

    audit_service.log_action(
        db, actor_user_id=user.id, action="PASSWORD_RESET_REQUESTED",
        entity_type="User", entity_id=user.id,
    )


def reset_password(db: Session, raw_token: str, new_password: str) -> User:
    token = password_reset_repository.get_by_token_hash(db, _hash_token(raw_token))
    now = datetime.now(timezone.utc)

    if token is None or token.used_at is not None or token.expires_at < now:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "This reset link is invalid or has expired.")

    user = user_repository.get_by_id(db, token.user_id)
    if user is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "This reset link is invalid or has expired.")

    user.password_hash = hash_password(new_password)
    # A verified reset is a stronger identity proof than the password
    # someone had been failing to guess — clear any lockout too.
    user.failed_login_count = 0
    user.locked_until = None
    token.used_at = now
    db.flush()

    audit_service.log_action(
        db, actor_user_id=user.id, action="PASSWORD_RESET_COMPLETED",
        entity_type="User", entity_id=user.id,
    )
    return user