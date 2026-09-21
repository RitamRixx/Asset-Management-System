"""
Service Contract model (Phase C).
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin


class ServiceContract(Base, TimestampMixin):
    __tablename__ = "service_contracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), index=True, nullable=False)
    vendor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("vendors.id"), index=True)

    contract_number: Mapped[Optional[str]] = mapped_column(String(100))
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))

    notes: Mapped[Optional[str]] = mapped_column(String(500))

    asset: Mapped["Asset"] = relationship() # noqa: F821
    vendor: Mapped[Optional["Vendor"]] = relationship() # noqa: F821
