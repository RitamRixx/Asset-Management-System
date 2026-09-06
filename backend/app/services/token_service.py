"""
Token revocation orchestration (IAM Phase 10).

`revoke_all_for_user` is the piece that was a documented stub through
Phase 9 — now real, because IssuedToken gives it something to iterate.
Called from: Admin disabling/suspending a user, self-service password
change, and a future explicit "log out everywhere" action if you want one
later (not built now — not asked for).
"""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.revoked_token import RevokedToken
from app.repositories import issued_token_repository, revoked_token_repository


def revoke_all_for_user(db: Session, user_id: int) -> int:
    """Returns the number of tokens revoked, mainly for audit/logging."""
    now = datetime.now(timezone.utc)
    active_tokens = issued_token_repository.list_active_for_user(db, user_id, now=now)

    for issued in active_tokens:
        revoked_token_repository.create(
            db,
            RevokedToken(jti=issued.jti, user_id=user_id, expires_at=issued.expires_at),
        )
    db.flush()
    return len(active_tokens)