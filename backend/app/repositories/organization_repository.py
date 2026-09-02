"""OrganizationSettings data-access layer (IAM Phase 8)."""
from app.models.organization import OrganizationSettings
from sqlalchemy.orm import Session


def get_or_create(db: Session) -> OrganizationSettings:
    settings_row = db.get(OrganizationSettings, 1)
    if settings_row is None:
        settings_row = OrganizationSettings(id=1)
        db.add(settings_row)
        db.flush()
    return settings_row