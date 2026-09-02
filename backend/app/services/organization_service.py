"""Organization settings business logic (IAM Phase 8)."""
from typing import Any

from sqlalchemy.orm import Session

from app.models.organization import OrganizationSettings
from app.repositories import organization_repository
from app.services import audit_service


def update_settings(db: Session, data: dict[str, Any], actor_user_id: int) -> OrganizationSettings:
    settings_row = organization_repository.get_or_create(db)
    old_value = {k: getattr(settings_row, k) for k in data.keys()}
    for key, value in data.items():
        setattr(settings_row, key, value)
    settings_row.updated_by = actor_user_id
    db.flush()

    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="ORGANIZATION_SETTINGS_UPDATED",
        entity_type="OrganizationSettings",
        entity_id=1,
        old_value={k: str(v) for k, v in old_value.items()},
        new_value={k: str(v) for k, v in data.items()},
    )
    return settings_row