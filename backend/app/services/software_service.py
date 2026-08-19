"""Software/license business logic (sections 17-18, business rules #11-12)."""
from datetime import date, datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enums import SoftwareAssignmentStatus
from app.models.software import SoftwareAssignment, SoftwareLicense
from app.repositories import software_repository
from app.services import audit_service


def assign_license(
    db: Session, *, employee_id: int, license_: SoftwareLicense, actor_user_id: int
) -> SoftwareAssignment:
    if license_.expiry_date is not None and license_.expiry_date < date.today():
        # Business rule #12.
        raise HTTPException(
            status.HTTP_409_CONFLICT, "This license has expired and cannot be newly assigned."
        )
    if license_.assigned_seats >= license_.seats:
        # Business rule #11.
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"No free seats left on this license ({license_.assigned_seats}/{license_.seats} in use).",
        )

    assignment = SoftwareAssignment(
        employee_id=employee_id,
        license_id=license_.id,
        status=SoftwareAssignmentStatus.ACTIVE,
    )
    software_repository.create_assignment(db, assignment)

    license_.assigned_seats += 1
    db.flush()

    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="SOFTWARE_ASSIGNED",
        entity_type="SoftwareAssignment",
        entity_id=assignment.id,
        new_value={"employee_id": employee_id, "license_id": license_.id},
    )
    return assignment


def revoke_assignment(
    db: Session, assignment: SoftwareAssignment, license_: SoftwareLicense, actor_user_id: int
) -> SoftwareAssignment:
    if assignment.status != SoftwareAssignmentStatus.ACTIVE:
        raise HTTPException(status.HTTP_409_CONFLICT, "This assignment is already revoked.")

    assignment.status = SoftwareAssignmentStatus.REVOKED
    assignment.revoked_at = datetime.now(timezone.utc)
    license_.assigned_seats = max(0, license_.assigned_seats - 1)
    db.flush()

    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="SOFTWARE_REVOKED",
        entity_type="SoftwareAssignment",
        entity_id=assignment.id,
        old_value={"status": "ACTIVE"},
        new_value={"status": "REVOKED"},
    )
    return assignment
