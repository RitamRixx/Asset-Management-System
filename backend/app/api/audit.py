"""Audit log router (section 31). Admin-only, read-only — no POST/PATCH/DELETE exist."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.database import get_db
from app.core.permissions import Role
from app.models.audit import AuditLog
from app.repositories import audit_repository
from app.schemas.audit import AuditLogRead

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("", response_model=list[AuditLogRead], dependencies=[Depends(require_role(Role.ADMIN))])
def list_audit_logs(
    entity_type: str | None = None,
    entity_id: int | None = None,
    actor_user_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[AuditLog]:
    return audit_repository.list_logs(
        db,
        entity_type=entity_type,
        entity_id=entity_id,
        actor_user_id=actor_user_id,
        skip=skip,
        limit=limit,
    )
