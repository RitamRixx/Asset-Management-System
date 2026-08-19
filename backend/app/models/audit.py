"""
AuditLog model (section 31 of the spec).

Append-only by convention: no service in this codebase ever issues an
UPDATE or DELETE against this table, and the audit API (Phase 14) only
exposes GET endpoints. old_value/new_value are stored as JSON text
snapshots rather than typed columns since the entity being audited varies.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[Optional[int]] = mapped_column()

    old_value: Mapped[Optional[dict]] = mapped_column(JSON)
    new_value: Mapped[Optional[dict]] = mapped_column(JSON)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ip_address: Mapped[Optional[str]] = mapped_column(String(64))
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSON)
