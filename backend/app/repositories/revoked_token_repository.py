"""RevokedToken data-access layer (IAM Phase 9)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.revoked_token import RevokedToken


def is_revoked(db: Session, jti: str) -> bool:
    return db.scalar(select(RevokedToken.id).where(RevokedToken.jti == jti)) is not None


def create(db: Session, token: RevokedToken) -> RevokedToken:
    db.add(token)
    db.flush()
    return token


def revoke_all_for_user(db: Session, user_id: int, *, revoked_at, expires_at) -> None:
    """Used when disabling/suspending a user (Phase 9 wiring into
    users.py) — not just logout. Without a live list of a user's
    *currently outstanding* jtis (this app doesn't track that; each is
    only recorded on logout, not on issue), this can't retroactively
    revoke a token nobody has explicitly logged out of yet. Documented
    as a known limitation below rather than silently incomplete."""
    pass  # intentionally not implemented — see docstring + CLAUDE.md note