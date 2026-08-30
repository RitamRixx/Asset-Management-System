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
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models.enums import UserStatus
from app.models.user import User
from app.repositories import user_repository


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Returns the User on success, None on any failure.

    Deliberately returns None (not a specific reason) for "no such user",
    "wrong password", AND "this account has no local password" (e.g. a
    Microsoft-only user) — the API layer turns this into one generic 401,
    so failed logins never leak *why* they failed, including whether an
    account exists locally at all or is SSO-only.
    """
    user = user_repository.get_by_email(db, email)
    if user is None:
        return None
    if user.password_hash is None:
        # Microsoft-provider (or otherwise passwordless) account hitting
        # the local login endpoint — reject cleanly, same as wrong password.
        return None
    if not verify_password(password, user.password_hash):
        return None
    if user.status != UserStatus.ACTIVE:
        return None

    user.last_login = datetime.now(timezone.utc)
    db.flush()
    return user