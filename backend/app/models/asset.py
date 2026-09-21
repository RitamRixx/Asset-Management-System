"""
Asset model (section 14 of the spec).

Deliberately has no `employee_id` / "current owner" column. Per section 20,
ownership is derived by looking at the latest active AssignmentItem for the
asset — that's what preserves full assignment history instead of
overwriting a single foreign key on every handover.

Warranty is modeled as its own table (see warranty.py) with a FK back to
Asset rather than a single `warranty_id` column here, so an asset can carry
more than one warranty record over its life (e.g. an extension) without
losing the earlier one.
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import AssetCondition, AssetStatus
from app.models.mixins import TimestampMixin


class Asset(Base, TimestampMixin):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    asset_type_id: Mapped[int] = mapped_column(ForeignKey("asset_types.id"), nullable=False, index=True)

    manufacturer: Mapped[Optional[str]] = mapped_column(String(100))
    model: Mapped[Optional[str]] = mapped_column(String(100))
    serial_number: Mapped[Optional[str]] = mapped_column(String(150), unique=True)

    purchase_date: Mapped[Optional[date]] = mapped_column(Date)
    purchase_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    vendor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("vendors.id"), index=True)

    status: Mapped[AssetStatus] = mapped_column(default=AssetStatus.AVAILABLE, nullable=False, index=True)
    condition: Mapped[AssetCondition] = mapped_column(default=AssetCondition.NEW, nullable=False)
    location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("locations.id"), index=True) # DEPRECATED
    org_unit_id: Mapped[Optional[int]] = mapped_column(ForeignKey("org_units.id"), index=True)
    org_unit: Mapped[Optional["OrgUnit"]] = relationship(foreign_keys=[org_unit_id]) # noqa: F821

    hostname: Mapped[Optional[str]] = mapped_column(String(150))
    description: Mapped[Optional[str]] = mapped_column(String(500))

    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, server_default='{}')
    salvage_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    useful_life_years: Mapped[Optional[int]] = mapped_column()

    NON_ASSIGNABLE_STATUSES = (AssetStatus.LOST, AssetStatus.RETIRED, AssetStatus.UNDER_REPAIR, AssetStatus.DISPOSED)

    @property
    def depreciated_value(self) -> Optional[Decimal]:
        if (
            self.purchase_cost is None
            or self.salvage_value is None
            or self.useful_life_years is None
            or self.useful_life_years <= 0
            or self.purchase_date is None
        ):
            return None
            
        from datetime import date
        years_passed = Decimal(str((date.today() - self.purchase_date).days / 365.25))
        if years_passed >= self.useful_life_years:
            return self.salvage_value
            
        depreciation_per_year = (self.purchase_cost - self.salvage_value) / Decimal(self.useful_life_years)
        current_value = self.purchase_cost - (years_passed * depreciation_per_year)
        return max(self.salvage_value, round(current_value, 2))
