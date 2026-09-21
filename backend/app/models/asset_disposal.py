"""
Asset Disposal model (Phase C).
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import DisposalMethod
from app.models.mixins import TimestampMixin


class AssetDisposal(Base, TimestampMixin):
    __tablename__ = "asset_disposals"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), unique=True, nullable=False)

    disposal_date: Mapped[date] = mapped_column(Date, nullable=False)
    disposal_method: Mapped[DisposalMethod] = mapped_column(nullable=False)
    disposal_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))

    authorized_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(500))

    asset: Mapped["Asset"] = relationship() # noqa: F821
    authorized_by: Mapped["User"] = relationship() # noqa: F821
