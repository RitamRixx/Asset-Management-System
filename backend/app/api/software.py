"""
Software & license router (sections 17-18).

IT/Admin manage the catalog, licenses, and assignments. Staff roles can
read. `/employees/{id}/software` additionally allows the employee to read
their own assignments (section 6: "View software assigned/installed to
them"), via the same `require_self_or_role` pattern the employees router
uses for rule #14.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role, require_self_or_role
from app.core.database import get_db
from app.core.permissions import Role
from app.models.software import Software, SoftwareAssignment, SoftwareLicense
from app.models.user import User
from app.repositories import software_repository
from app.schemas.software import (
    LicenseCreate,
    LicenseRead,
    SoftwareAssignmentCreate,
    SoftwareAssignmentRead,
    SoftwareCreate,
    SoftwareRead,
)
from app.services import software_service

router = APIRouter(tags=["software"])

STAFF_ROLES = (Role.ADMIN, Role.HR, Role.IT_SUPPORT)
MANAGE_ROLES = (Role.ADMIN, Role.IT_SUPPORT)


@router.post(
    "/software", response_model=SoftwareRead, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(*MANAGE_ROLES))],
)
def create_software(payload: SoftwareCreate, db: Session = Depends(get_db)) -> Software:
    software = Software(**payload.model_dump())
    software_repository.create_software(db, software)
    db.commit()
    db.refresh(software)
    return software


@router.get("/software", response_model=list[SoftwareRead], dependencies=[Depends(require_role(*STAFF_ROLES))])
def list_software(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)) -> list[Software]:
    return software_repository.list_software(db, skip=skip, limit=limit)


@router.post(
    "/licenses", response_model=LicenseRead, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(*MANAGE_ROLES))],
)
def create_license(payload: LicenseCreate, db: Session = Depends(get_db)) -> SoftwareLicense:
    license_ = SoftwareLicense(**payload.model_dump())
    software_repository.create_license(db, license_)
    db.commit()
    db.refresh(license_)
    return license_


@router.get("/licenses", response_model=list[LicenseRead], dependencies=[Depends(require_role(*STAFF_ROLES))])
def list_licenses(
    software_id: int | None = None, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)
) -> list[SoftwareLicense]:
    return software_repository.list_licenses(db, software_id=software_id, skip=skip, limit=limit)


@router.post(
    "/software-assignments",
    response_model=SoftwareAssignmentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(*MANAGE_ROLES))],
)
def assign_license(
    payload: SoftwareAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SoftwareAssignment:
    license_ = software_repository.get_license(db, payload.license_id)
    if license_ is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "License not found")

    assignment = software_service.assign_license(
        db, employee_id=payload.employee_id, asset_id=payload.asset_id, license_=license_, actor_user_id=current_user.id
    )
    db.commit()
    db.refresh(assignment)
    return assignment


@router.post(
    "/software-assignments/{assignment_id}/revoke",
    response_model=SoftwareAssignmentRead,
    dependencies=[Depends(require_role(*MANAGE_ROLES))],
)
def revoke_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SoftwareAssignment:
    assignment = software_repository.get_assignment(db, assignment_id)
    if assignment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Assignment not found")
    license_ = software_repository.get_license(db, assignment.license_id)

    assignment = software_service.revoke_assignment(db, assignment, license_, current_user.id)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.get(
    "/employees/{employee_id}/software",
    response_model=list[SoftwareAssignmentRead],
    dependencies=[Depends(require_self_or_role("employee_id", *STAFF_ROLES))],
)
def list_employee_software(employee_id: int, db: Session = Depends(get_db)) -> list[SoftwareAssignment]:
    return software_repository.list_assignments_for_employee(db, employee_id)


@router.get(
    "/assets/{asset_id}/software",
    response_model=list[SoftwareAssignmentRead],
    dependencies=[Depends(require_role(*STAFF_ROLES))],
)
def list_asset_software(asset_id: int, db: Session = Depends(get_db)) -> list[SoftwareAssignment]:
    # We will need to implement list_assignments_for_asset in software_repository
    return software_repository.list_assignments_for_asset(db, asset_id)


@router.get(
    "/licenses/{license_id}/key",
    dependencies=[Depends(require_role(*MANAGE_ROLES))],
)
def get_license_key(
    license_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str | None]:
    license_ = software_repository.get_license(db, license_id)
    if license_ is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "License not found")

    from app.services import audit_service
    audit_service.log_action(
        db,
        actor_user_id=current_user.id,
        action="LICENSE_KEY_VIEWED",
        entity_type="SoftwareLicense",
        entity_id=license_.id,
        new_value={"key_viewed": True},
    )
    db.commit()

    return {"license_key": license_.license_key}
