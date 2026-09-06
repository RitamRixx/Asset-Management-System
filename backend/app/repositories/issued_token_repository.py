"""IssuedToken data-access layer (IAM Phase 10)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.issued_token import IssuedToken


def create(db: Session, token: IssuedToken) -> IssuedToken:
    db.add(token)
    db.flush()
    return token


def list_active_for_user(db: Session, user_id: int, *, now) -> list[IssuedToken]:
    """Only jtis that haven't naturally expired yet are worth revoking —
    no point writing a denylist row for a token that's already dead."""
    stmt = select(IssuedToken).where(
        IssuedToken.user_id == user_id, IssuedToken.expires_at > now
    )
    return list(db.scalars(stmt))