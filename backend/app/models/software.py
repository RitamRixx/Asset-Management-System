"""Software catalog, licenses, and per-employee license assignment (sections 17-18)."""
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import LicenseStatus, SoftwareAssignmentStatus
from app.models.mixins import TimestampMixin


class Software(Base, TimestampMixin):
    __tablename__ = "software"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    publisher: Mapped[Optional[str]] = mapped_column(String(150))
    version: Mapped[Optional[str]] = mapped_column(String(50))
    category: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(500))


class SoftwareLicense(Base, TimestampMixin):
    __tablename__ = "software_licenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    software_id: Mapped[int] = mapped_column(ForeignKey("software.id"), nullable=False)

    # The full key/reference is stored here but section 18 says it must
    # never be *exposed* to unauthorized users — that redaction happens in
    # the Pydantic response schema (see schemas/license.py), not here.
    license_key: Mapped[Optional[str]] = mapped_column(String(255))
    license_type: Mapped[Optional[str]] = mapped_column(String(50))

    seats: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    assigned_seats: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    purchase_date: Mapped[Optional[date]] = mapped_column(Date)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    vendor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("vendors.id"))
    status: Mapped[LicenseStatus] = mapped_column(default=LicenseStatus.ACTIVE, nullable=False)


class SoftwareAssignment(Base, TimestampMixin):
    """Which employee currently has which license seat (section 17's
    'which software is assigned to an employee' question)."""

    __tablename__ = "software_assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    license_id: Mapped[int] = mapped_column(ForeignKey("software_licenses.id"), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[SoftwareAssignmentStatus] = mapped_column(
        default=SoftwareAssignmentStatus.ACTIVE, nullable=False
    )
