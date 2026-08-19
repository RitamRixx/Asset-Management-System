"""
Configurable lookup tables (section 13: asset types must not be hardcoded
in frontend logic — they're admin-manageable rows here instead).
"""
from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin


class AssetType(Base, TimestampMixin):
    __tablename__ = "asset_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)


class ComponentType(Base, TimestampMixin):
    __tablename__ = "component_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)
