"""OrgUnit router (Phase A)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.core.permissions import Role
from app.models.user import User
from app.repositories import org_unit_repository
from app.schemas.reference import OrgUnitCreate, OrgUnitRead
from app.services import org_unit_service

router = APIRouter(prefix="/org-units", tags=["org-units"])
STAFF_ROLES = (Role.ADMIN, Role.HR, Role.IT_SUPPORT)

@router.post("", response_model=OrgUnitRead, dependencies=[Depends(require_role(Role.ADMIN))])
def create_org_unit(
    payload: OrgUnitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    unit = org_unit_service.create_org_unit(
        db=db,
        name=payload.name,
        code=payload.code,
        unit_type_id=payload.unit_type_id,
        parent_id=payload.parent_id,
        address=payload.address,
        city=payload.city,
        state=payload.state,
        country=payload.country,
        manager_id=payload.manager_id,
        actor_user_id=current_user.id,
    )
    db.commit()
    db.refresh(unit)
    return unit

@router.get("", response_model=list[OrgUnitRead], dependencies=[Depends(require_role(*STAFF_ROLES))])
def list_org_units(db: Session = Depends(get_db)):
    return org_unit_repository.get_all(db)

@router.get("/{org_unit_id}/subtree", response_model=list[OrgUnitRead], dependencies=[Depends(require_role(*STAFF_ROLES))])
def get_subtree(org_unit_id: int, db: Session = Depends(get_db)):
    return org_unit_repository.get_subtree(db, org_unit_id)

@router.get("/{org_unit_id}/ancestors", response_model=list[OrgUnitRead], dependencies=[Depends(require_role(*STAFF_ROLES))])
def get_ancestors(org_unit_id: int, db: Session = Depends(get_db)):
    return org_unit_repository.get_ancestors(db, org_unit_id)
