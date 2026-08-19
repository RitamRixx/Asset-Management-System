"""Audit log data-access layer (section 31). Read-only by design — no
update()/delete() function exists here, matching the append-only table."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def list_logs(
    db: Session,
    *,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    actor_user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[AuditLog]:
    stmt = select(AuditLog)
    if entity_type is not None:
        stmt = stmt.where(AuditLog.entity_type == entity_type)
    if entity_id is not None:
        stmt = stmt.where(AuditLog.entity_id == entity_id)
    if actor_user_id is not None:
        stmt = stmt.where(AuditLog.actor_user_id == actor_user_id)
    stmt = stmt.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt))
