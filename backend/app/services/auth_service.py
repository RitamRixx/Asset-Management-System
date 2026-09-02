# """Auth business logic (Phase 4)."""
# from datetime import datetime, timezone
# from typing import Optional

# from sqlalchemy.orm import Session

# from app.core.security import verify_password
# from app.models.enums import UserStatus
# from app.models.user import User
# from app.repositories import user_repository


# def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
#     """Returns the User on success, None on any failure.

#     Deliberately returns None (not a specific reason) for both "no such
#     user" and "wrong password" — the API layer turns this into one generic
#     401, so failed logins don't leak which part was wrong.
#     """
#     user = user_repository.get_by_email(db, email)
#     if user is None:
#         return None
#     if not verify_password(password, user.password_hash):
#         return None
#     if user.status != UserStatus.ACTIVE:
#         return None

#     user.last_login = datetime.now(timezone.utc)
#     db.flush()
#     return user

"""Auth business logic (Phase 4)."""
# from datetime import datetime, timezone
# from typing import Optional

# from sqlalchemy.orm import Session

# from app.core.security import verify_password
# from app.models.enums import UserStatus
# from app.models.user import User
# from app.repositories import user_repository


# def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
#     """Returns the User on success, None on any failure.

#     Deliberately returns None (not a specific reason) for "no such user",
#     "wrong password", AND "this account has no local password" (e.g. a
#     Microsoft-only user) — the API layer turns this into one generic 401,
#     so failed logins never leak *why* they failed, including whether an
#     account exists locally at all or is SSO-only.
#     """
#     user = user_repository.get_by_email(db, email)
#     if user is None:
#         return None
#     if user.password_hash is None:
#         # Microsoft-provider (or otherwise passwordless) account hitting
#         # the local login endpoint — reject cleanly, same as wrong password.
#         return None
#     if not verify_password(password, user.password_hash):
#         return None
#     if user.status != UserStatus.ACTIVE:
#         return None

#     user.last_login = datetime.now(timezone.utc)
#     db.flush()
#     return user


"""Auth business logic (Phase 4; extended IAM Phase 4 with account lockout)."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import verify_password
from app.models.enums import UserStatus
from app.models.user import User
from app.repositories import user_repository


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Returns the User on success, None on any failure — including a
    locked-out account. Every failure path returns None so the API layer's
    single generic 401 never leaks *why* it failed (same principle as the
    password_hash-is-None guard from the SSO phase — lockout state is just
    one more thing that must not leak).
    """
    user = user_repository.get_by_email(db, email)
    if user is None:
        return None
    if user.password_hash is None:
        return None

    now = datetime.now(timezone.utc)
    if user.locked_until is not None and user.locked_until > now:
        return None

    if not verify_password(password, user.password_hash):
        user.failed_login_count += 1
        if user.failed_login_count >= settings.LOGIN_LOCKOUT_THRESHOLD:
            user.locked_until = now + timedelta(minutes=settings.LOGIN_LOCKOUT_DURATION_MINUTES)
        db.flush()
        return None

    if user.status != UserStatus.ACTIVE:
        return None

    user.failed_login_count = 0
    user.locked_until = None
    user.last_login = now
    db.flush()
    return user