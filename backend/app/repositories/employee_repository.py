"""Employee data-access layer."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.enums import EmploymentStatus


def get_by_id(db: Session, employee_id: int) -> Optional[Employee]:
    return db.get(Employee, employee_id)


def get_by_email(db: Session, email: str) -> Optional[Employee]:
    return db.scalar(select(Employee).where(Employee.email == email))


def list_employees(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    department_id: Optional[int] = None,
    org_unit_id: Optional[int] = None,
    status_filter: Optional[EmploymentStatus] = None,
) -> list[Employee]:
    stmt = select(Employee)
    if department_id is not None:
        stmt = stmt.where(Employee.department_id == department_id)
    if org_unit_id is not None:
        stmt = stmt.where(Employee.org_unit_id == org_unit_id)
    if status_filter is not None:
        stmt = stmt.where(Employee.employment_status == status_filter)
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt))


def create(db: Session, employee: Employee) -> Employee:
    db.add(employee)
    db.flush()
    return employee
