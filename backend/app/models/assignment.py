"""
Assignment models (sections 19-21 of the spec).

An `AssetAssignment` is one handover transaction to one employee (e.g. "new
joiner receives laptop + charger + monitor in one go"). Each physical asset
in that handover is its own `AssignmentItem` row, so items can later be
returned or transferred independently while the transaction they arrived in
stays intact.

"Who currently holds asset X" is answered by: the AssignmentItem for that
asset_id with status=ACTIVE and the latest assigned_at.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import AssetCondition, AssignmentStatus, ReturnCondition
from app.models.mixins import TimestampMixin


class AssetAssignment(Base, TimestampMixin):
    __tablename__ = "asset_assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    assigned_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expected_return_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    notes: Mapped[Optional[str]] = mapped_column(String(500))

    items: Mapped[list["AssignmentItem"]] = relationship(
        back_populates="assignment", order_by="AssignmentItem.id"
    )


class AssignmentItem(Base, TimestampMixin):
    __tablename__ = "assignment_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    assignment_id: Mapped[int] = mapped_column(
        ForeignKey("asset_assignments.id"), nullable=False
    )
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False)

    condition_at_assignment: Mapped[Optional[AssetCondition]] = mapped_column()
    status: Mapped[AssignmentStatus] = mapped_column(
        default=AssignmentStatus.ACTIVE, nullable=False
    )

    returned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    return_condition: Mapped[Optional[ReturnCondition]] = mapped_column()
    notes: Mapped[Optional[str]] = mapped_column(String(500))

    assignment: Mapped["AssetAssignment"] = relationship(back_populates="items")
