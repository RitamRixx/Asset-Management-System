"""DeviceAgent data-access layer (section 37)."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.device_agent import DeviceAgent


def get_by_device_id(db: Session, device_id: str) -> Optional[DeviceAgent]:
    return db.scalar(select(DeviceAgent).where(DeviceAgent.device_id == device_id))


def get_by_token_hash(db: Session, token_hash: str) -> Optional[DeviceAgent]:
    return db.scalar(select(DeviceAgent).where(DeviceAgent.registration_token_hash == token_hash))


def create(db: Session, device_agent: DeviceAgent) -> DeviceAgent:
    db.add(device_agent)
    db.flush()
    return device_agent
