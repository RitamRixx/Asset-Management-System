"""
Agent business logic (section 37 of the spec).

Registration is gated behind IT/Admin auth (an IT staff member registers a
device against an asset and hands the returned token to whatever gets
installed on that machine) rather than open self-registration — a
reasonable secure default for groundwork that explicitly isn't meant to be
a finished device-provisioning system yet.
"""
import hashlib
import secrets

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.device_agent import DeviceAgent
from app.models.enums import DeviceAgentStatus
from app.repositories import device_agent_repository
from app.services import audit_service


def _hash_token(raw_token: str) -> str:
    # SHA-256 (not Argon2): this is a high-entropy random token, not a
    # human-chosen password, so a fast hash is the right tool — Argon2's
    # deliberate slowness defends against guessing low-entropy secrets,
    # which doesn't apply here and would just add needless latency.
    return hashlib.sha256(raw_token.encode()).hexdigest()


def register_device(
    db: Session, *, device_id: str, asset_id: int | None, agent_version: str | None, actor_user_id: int
) -> tuple[DeviceAgent, str]:
    if device_agent_repository.get_by_device_id(db, device_id) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, f"Device {device_id} is already registered.")

    raw_token = secrets.token_urlsafe(32)
    device_agent = DeviceAgent(
        device_id=device_id,
        asset_id=asset_id,
        agent_version=agent_version,
        registration_token_hash=_hash_token(raw_token),
        status=DeviceAgentStatus.ACTIVE,
    )
    device_agent_repository.create(db, device_agent)

    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="DEVICE_AGENT_REGISTERED",
        entity_type="DeviceAgent",
        entity_id=device_agent.id,
        new_value={"device_id": device_id, "asset_id": asset_id},
    )
    return device_agent, raw_token


def authenticate_device(db: Session, raw_token: str) -> DeviceAgent:
    device_agent = device_agent_repository.get_by_token_hash(db, _hash_token(raw_token))
    if device_agent is None or device_agent.status != DeviceAgentStatus.ACTIVE:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or inactive device token.")
    return device_agent
