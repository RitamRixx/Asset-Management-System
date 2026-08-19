"""
Centralized audit logging (section 31 of the spec).

Every service that performs a "critical change" (rule #15) calls
`log_action` as part of the same DB transaction as the change itself, so
the audit trail and the mutation always commit or roll back together.
Nothing outside this module ever writes to `audit_logs`.
"""
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def log_action(
    db: Session,
    *,
    actor_user_id: Optional[int],
    action: str,
    entity_type: str,
    entity_id: Optional[int],
    old_value: Optional[dict[str, Any]] = None,
    new_value: Optional[dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    extra_metadata: Optional[dict[str, Any]] = None,
) -> AuditLog:
    entry = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address,
        extra_metadata=extra_metadata,
    )
    db.add(entry)
    db.flush()
    return entry
