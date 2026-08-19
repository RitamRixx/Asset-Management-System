"""
AssetTransfer model (section 22 of the spec).

A transfer is recorded as its own entity rather than mutating an
assignment's employee_id. The transfer service (Phase 11) will, on
completion: close the source AssignmentItem (status=TRANSFERRED), open a
new AssetAssignment/AssignmentItem for the destination employee, and write
an audit log — so both the old and new ownership remain visible.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import TransferStatus
from app.models.mixins import TimestampMixin


class AssetTransfer(Base, TimestampMixin):
    __tablename__ = "asset_transfers"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False)
    from_employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    to_employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)

    requested_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    approved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    status: Mapped[TransferStatus] = mapped_column(
        default=TransferStatus.PENDING, nullable=False
    )
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    notes: Mapped[Optional[str]] = mapped_column(String(500))
