"""PasswordResetToken data-access layer (IAM Phase 4)."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.password_reset import PasswordResetToken


def create(db: Session, token: PasswordResetToken) -> PasswordResetToken:
    db.add(token)
    db.flush()
    return token


def get_by_token_hash(db: Session, token_hash: str) -> Optional[PasswordResetToken]:
    return db.scalar(select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash))