"""
PasswordResetToken model (IAM Phase 2; consumed by the forgot/reset-
password flow in a later phase).

Tokens are never stored raw — only a SHA-256 hash of what the user
actually receives, mirroring the DeviceAgent registration-token pattern
already used elsewhere in this codebase (see services/agent_service.py).
Kept as its own table rather than columns on User: reset activity is
naturally row-like (created, expires, superseded), and this avoids
growing `users` with fields that are live for a tiny fraction of a
user's lifetime.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))