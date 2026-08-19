"""
Warranty model (section 27 of the spec).

No stored `status` column: "the system should calculate expiry status
based on dates" (spec's own words), so ACTIVE / EXPIRING / EXPIRED is a
computed property here, evaluated fresh on every read instead of drifting
out of sync with warranty_end.
"""
from datetime import date, timedelta
from typing import Optional

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin

EXPIRING_SOON_WINDOW_DAYS = 30


class Warranty(Base, TimestampMixin):
    __tablename__ = "warranties"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False)
    warranty_start: Mapped[Optional[date]] = mapped_column(Date)
    warranty_end: Mapped[Optional[date]] = mapped_column(Date)
    vendor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("vendors.id"))
    warranty_type: Mapped[Optional[str]] = mapped_column(String(100))
    warranty_reference: Mapped[Optional[str]] = mapped_column(String(150))

    @property
    def computed_status(self) -> str:
        if self.warranty_end is None:
            return "UNKNOWN"
        today = date.today()
        if self.warranty_end < today:
            return "EXPIRED"
        if self.warranty_end <= today + timedelta(days=EXPIRING_SOON_WINDOW_DAYS):
            return "EXPIRING_SOON"
        return "ACTIVE"
