"""
OrganizationSettings model (IAM Phase 8).

Singleton row (id always 1, enforced by a CHECK constraint — see the
migration) backing what the frontend's BrandContext/Settings page
previously kept in localStorage only. `email_notifications_default` is
the org-wide default; a later phase could add a per-user override without
changing this table.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class OrganizationSettings(Base):
    __tablename__ = "organization_settings"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    company_name: Mapped[str] = mapped_column(String(150), default="AMS Platform", nullable=False)
    tagline: Mapped[Optional[str]] = mapped_column(String(255))
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    email_notifications_default: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )