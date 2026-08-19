"""
Agent API schemas (section 37).

The spec is explicit: design this now, don't implement the actual Windows
Asset Agent. These schemas are intentionally minimal — just enough shape
for `/agent/*` endpoints to exist and be exercised by future agent
development, not a finished device-management protocol.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import DeviceAgentStatus


class AgentRegisterRequest(BaseModel):
    device_id: str
    asset_id: Optional[int] = None
    agent_version: Optional[str] = None


class AgentRegisterResponse(BaseModel):
    device_id: str
    # Returned exactly once, at registration time — only the hash is ever
    # stored (see models/device_agent.py), mirroring password handling.
    registration_token: str


class AgentHeartbeatRequest(BaseModel):
    agent_version: Optional[str] = None


class DeviceAgentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    asset_id: Optional[int]
    last_seen: Optional[datetime]
    agent_version: Optional[str]
    status: DeviceAgentStatus
    registered_at: datetime


class AgentInventoryPayload(BaseModel):
    """Placeholder shape for section 37's future hardware inventory push
    (CPU/RAM/SSD/GPU/BIOS/etc). Accepted and audit-logged, not yet parsed
    into AssetComponent rows — that mapping is real product work for when
    the actual agent exists."""

    raw_payload: dict


class AgentSoftwarePayload(BaseModel):
    """Placeholder shape for the future installed-software push."""

    raw_payload: dict


class AgentConfigResponse(BaseModel):
    heartbeat_interval_seconds: int = 300
    inventory_interval_seconds: int = 86400
