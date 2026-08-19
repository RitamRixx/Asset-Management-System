"""
Agent router (section 37 of the spec).

Explicitly foundational: `/agent/inventory` and `/agent/software` accept
and audit-log a payload but don't parse it into AssetComponent/Software
rows yet — that mapping is real product work for whenever the actual
Windows Asset Agent is built, which the spec says not to do in this phase.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.core.permissions import Role
from app.models.device_agent import DeviceAgent
from app.models.user import User
from app.schemas.agent import (
    AgentConfigResponse,
    AgentHeartbeatRequest,
    AgentInventoryPayload,
    AgentRegisterRequest,
    AgentRegisterResponse,
    AgentSoftwarePayload,
    DeviceAgentRead,
)
from app.services import agent_service, audit_service

router = APIRouter(prefix="/agent", tags=["agent"])


def get_current_device(
    x_device_token: str = Header(..., description="Bearer-style device registration token"),
    db: Session = Depends(get_db),
) -> DeviceAgent:
    return agent_service.authenticate_device(db, x_device_token)


@router.post(
    "/register",
    response_model=AgentRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.ADMIN, Role.IT_SUPPORT))],
)
def register_device(
    payload: AgentRegisterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AgentRegisterResponse:
    device_agent, raw_token = agent_service.register_device(
        db,
        device_id=payload.device_id,
        asset_id=payload.asset_id,
        agent_version=payload.agent_version,
        actor_user_id=current_user.id,
    )
    db.commit()
    return AgentRegisterResponse(device_id=device_agent.device_id, registration_token=raw_token)


@router.post("/heartbeat", response_model=DeviceAgentRead)
def heartbeat(
    payload: AgentHeartbeatRequest,
    db: Session = Depends(get_db),
    device: DeviceAgent = Depends(get_current_device),
) -> DeviceAgent:
    device.last_seen = datetime.now(timezone.utc)
    if payload.agent_version:
        device.agent_version = payload.agent_version
    db.commit()
    db.refresh(device)
    return device


@router.post("/inventory", status_code=status.HTTP_202_ACCEPTED)
def push_inventory(
    payload: AgentInventoryPayload,
    db: Session = Depends(get_db),
    device: DeviceAgent = Depends(get_current_device),
) -> dict:
    audit_service.log_action(
        db,
        actor_user_id=None,
        action="DEVICE_INVENTORY_RECEIVED",
        entity_type="DeviceAgent",
        entity_id=device.id,
        new_value={"asset_id": device.asset_id, "payload_keys": list(payload.raw_payload.keys())},
    )
    db.commit()
    return {"status": "accepted", "note": "Inventory parsing is not implemented in this phase."}


@router.post("/software", status_code=status.HTTP_202_ACCEPTED)
def push_software(
    payload: AgentSoftwarePayload,
    db: Session = Depends(get_db),
    device: DeviceAgent = Depends(get_current_device),
) -> dict:
    audit_service.log_action(
        db,
        actor_user_id=None,
        action="DEVICE_SOFTWARE_RECEIVED",
        entity_type="DeviceAgent",
        entity_id=device.id,
        new_value={"asset_id": device.asset_id, "payload_keys": list(payload.raw_payload.keys())},
    )
    db.commit()
    return {"status": "accepted", "note": "Software inventory parsing is not implemented in this phase."}


@router.get("/config", response_model=AgentConfigResponse)
def get_config(device: DeviceAgent = Depends(get_current_device)) -> AgentConfigResponse:
    return AgentConfigResponse()
