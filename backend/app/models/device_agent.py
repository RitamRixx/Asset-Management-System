"""
DeviceAgent model — schema groundwork for section 37's future Windows
Asset Agent. Nothing in this codebase writes to this table yet except the
placeholder /api/v1/agent/register stub added in Phase 21; the actual
agent is explicitly out of scope per the spec.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import DeviceAgentStatus


class DeviceAgent(Base):
    __tablename__ = "device_agents"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    asset_id: Mapped[Optional[int]] = mapped_column(ForeignKey("assets.id"), index=True)

    # Never store the raw token — only its hash (mirrors password handling).
    registration_token_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    agent_version: Mapped[Optional[str]] = mapped_column(String(30))
    status: Mapped[DeviceAgentStatus] = mapped_column(
        default=DeviceAgentStatus.PENDING, nullable=False
    )
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
