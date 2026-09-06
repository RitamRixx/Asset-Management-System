"""
IssuedToken model (IAM Phase 10).

Every access token minted by create_access_token gets a row here at
issue-time, alongside its jti. This is what makes mass-revocation
possible: revoked_tokens (Phase 9) is a denylist you can only add
*specific* jtis to, and without a record of which jtis exist for a given
user, "revoke everything user X currently holds" has nothing to iterate
over. This table is that missing list. Deliberately separate from
RevokedToken rather than a boolean column on one table — issuance and
revocation are different events with different retention needs (an issued
row is written on every single login; a revoked row only on the rarer
explicit-revocation path).
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class IssuedToken(Base):
    __tablename__ = "issued_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    jti: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)