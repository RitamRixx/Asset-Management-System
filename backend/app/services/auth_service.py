"""Auth business logic (Phase 4; extended IAM Phase 5 with lockout)."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import verify_password
from app.models.enums import UserStatus
from app.models.user import User
from app.repositories import user_repository
from app.services import audit_service


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Returns the User on success, None on any failure — including a
    locked account, so a locked-out attempt looks identical to a wrong
    password from the outside (no separate "account locked" signal is
    ever leaked pre-auth).
    """
    user = user_repository.get_by_email(db, email)
    if user is None:
        return None
    if user.password_hash is None:
        return None
    if user.status != UserStatus.ACTIVE:
        return None

    now = datetime.now(timezone.utc)
    if user.locked_until is not None and user.locked_until > now:
        return None

    if not verify_password(password, user.password_hash):
        user.failed_login_count += 1
        if user.failed_login_count >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
            user.locked_until = now + timedelta(minutes=settings.LOCKOUT_DURATION_MINUTES)
            audit_service.log_action(
                db, actor_user_id=user.id, action="USER_LOCKED_OUT", entity_type="User", entity_id=user.id,
                new_value={"failed_login_count": user.failed_login_count, "locked_until": user.locked_until.isoformat()},
            )
        db.flush()
        return None

    # Successful login clears any prior lockout state.
    user.failed_login_count = 0
    user.locked_until = None
    user.last_login = now
    db.flush()
    return user