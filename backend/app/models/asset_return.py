"""
AssetReturn model (section 23 of the spec).

Distinct from AssignmentItem.returned_at/return_condition: this table is
the IT-verification record of the physical handback (who returned it, who
received/inspected it, any notes) and is what the return service inserts
alongside closing the AssignmentItem. Keeping it separate lets a return be
audited/reported on its own without joining through the assignment.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import ReturnCondition
from app.models.mixins import TimestampMixin


class AssetReturn(Base, TimestampMixin):
    __tablename__ = "asset_returns"

    id: Mapped[int] = mapped_column(primary_key=True)
    assignment_item_id: Mapped[int] = mapped_column(
        ForeignKey("assignment_items.id"), nullable=False
    )
    returned_by_employee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("employees.id"), index=True)
    received_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    return_condition: Mapped[ReturnCondition] = mapped_column(nullable=False)
    returned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    notes: Mapped[Optional[str]] = mapped_column(String(500))
