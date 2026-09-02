"""
Organization settings router (IAM Phase 8).

GET is open to any authenticated user — branding needs to render in
every role's sidebar. PATCH is Admin-only, matching the rest of this
app's reference-data write pattern.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.core.permissions import Role
from app.models.organization import OrganizationSettings
from app.models.user import User
from app.repositories import organization_repository
from app.schemas.organization import OrganizationRead, OrganizationUpdate
from app.services import organization_service

router = APIRouter(prefix="/organization", tags=["organization"])


@router.get("", response_model=OrganizationRead)
def get_organization(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> OrganizationSettings:
    return organization_repository.get_or_create(db)


@router.patch("", response_model=OrganizationRead, dependencies=[Depends(require_role(Role.ADMIN))])
def update_organization(
    payload: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrganizationSettings:
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    settings_row = organization_service.update_settings(db, updates, current_user.id)
    db.commit()
    db.refresh(settings_row)
    return settings_row