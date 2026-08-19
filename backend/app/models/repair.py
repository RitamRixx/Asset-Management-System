"""Repair workflow models (sections 25-26 of the spec)."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import RepairPriority, RepairStatus
from app.models.mixins import TimestampMixin


class RepairTicket(Base, TimestampMixin):
    __tablename__ = "repair_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False)
    reported_by: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)

    issue: Mapped[str] = mapped_column(String(1000), nullable=False)
    priority: Mapped[RepairPriority] = mapped_column(
        default=RepairPriority.MEDIUM, nullable=False
    )
    status: Mapped[RepairStatus] = mapped_column(default=RepairStatus.OPEN, nullable=False)

    diagnosis: Mapped[Optional[str]] = mapped_column(String(1000))
    vendor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("vendors.id"))
    repair_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    repair_start_date: Mapped[Optional[date]] = mapped_column(Date)
    repair_end_date: Mapped[Optional[date]] = mapped_column(Date)
    resolution: Mapped[Optional[str]] = mapped_column(String(1000))


class RepairHistory(Base):
    """Append-only status-transition log for a repair ticket."""

    __tablename__ = "repair_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    repair_ticket_id: Mapped[int] = mapped_column(
        ForeignKey("repair_tickets.id"), nullable=False
    )
    from_status: Mapped[Optional[RepairStatus]] = mapped_column()
    to_status: Mapped[RepairStatus] = mapped_column(nullable=False)
    changed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    notes: Mapped[Optional[str]] = mapped_column(String(500))
