"""Software/license/assignment data-access layer."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import SoftwareAssignmentStatus
from app.models.software import Software, SoftwareAssignment, SoftwareLicense


def get_software(db: Session, software_id: int) -> Optional[Software]:
    return db.get(Software, software_id)


def list_software(db: Session, skip: int = 0, limit: int = 50) -> list[Software]:
    return list(db.scalars(select(Software).offset(skip).limit(limit).order_by(Software.id)))


def create_software(db: Session, software: Software) -> Software:
    db.add(software)
    db.flush()
    return software


def get_license(db: Session, license_id: int) -> Optional[SoftwareLicense]:
    return db.get(SoftwareLicense, license_id)


def list_licenses(
    db: Session, software_id: Optional[int] = None, skip: int = 0, limit: int = 50
) -> list[SoftwareLicense]:
    stmt = select(SoftwareLicense)
    if software_id is not None:
        stmt = stmt.where(SoftwareLicense.software_id == software_id)
    stmt = stmt.offset(skip).limit(limit).order_by(SoftwareLicense.id)
    return list(db.scalars(stmt))


def create_license(db: Session, license_: SoftwareLicense) -> SoftwareLicense:
    db.add(license_)
    db.flush()
    return license_


def list_assignments_for_employee(db: Session, employee_id: int) -> list[SoftwareAssignment]:
    stmt = select(SoftwareAssignment).where(
        SoftwareAssignment.employee_id == employee_id,
        SoftwareAssignment.status == SoftwareAssignmentStatus.ACTIVE,
    )
    return list(db.scalars(stmt))


def get_assignment(db: Session, assignment_id: int) -> Optional[SoftwareAssignment]:
    return db.get(SoftwareAssignment, assignment_id)


def create_assignment(db: Session, assignment: SoftwareAssignment) -> SoftwareAssignment:
    db.add(assignment)
    db.flush()
    return assignment
