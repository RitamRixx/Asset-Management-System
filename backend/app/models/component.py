"""
AssetComponent model (sections 15-16 of the spec).

Replacing a component does NOT overwrite a row. It:
  1. Sets `removed_at` and `status=REMOVED` on the old component row.
  2. Inserts a new component row with `status=ACTIVE`.
  3. Sets the old row's `replaced_by_component_id` to the new row's id.

That chain is the component history — no separate history table needed;
querying all AssetComponent rows for an asset_id (including REMOVED ones)
already gives the full timeline described in section 16.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import ComponentStatus
from app.models.mixins import TimestampMixin


class AssetComponent(Base, TimestampMixin):
    __tablename__ = "asset_components"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False, index=True)
    component_type_id: Mapped[int] = mapped_column(
        ForeignKey("component_types.id"), nullable=False
    )

    # Free-text spec, e.g. "16 GB", "512 GB NVMe". Kept simple rather than
    # over-normalizing into separate size/unit columns.
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    serial_number: Mapped[Optional[str]] = mapped_column(String(150))

    status: Mapped[ComponentStatus] = mapped_column(
        default=ComponentStatus.ACTIVE, nullable=False
    )
    installed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    removed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    replaced_by_component_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("asset_components.id")
    )
