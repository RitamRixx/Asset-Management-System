"""
Employees router.

Create/edit: HR or Admin (section 4/5). IT can view (needs it for
assignments). Employee can view/list only their own record (rule #14).
"""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role, require_self_or_role
from app.core.database import get_db
from app.core.permissions import Role
from app.models.employee import Employee
from app.models.enums import EmploymentStatus
from app.models.user import User
from app.repositories import employee_repository
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeRead,
    EmployeeStatusUpdate,
    EmployeeUpdate,
)
from app.schemas.import_result import ImportResult
from app.services import employee_service, import_service

router = APIRouter(prefix="/employees", tags=["employees"])

STAFF_ROLES = (Role.ADMIN, Role.HR, Role.IT_SUPPORT)


@router.post(
    "",
    response_model=EmployeeRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(Role.ADMIN, Role.HR))],
)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Employee:
    if employee_repository.get_by_email(db, payload.email) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "An employee with this email already exists")

    employee = employee_service.create_employee(db, payload.model_dump(), current_user.id)
    db.commit()
    db.refresh(employee)
    return employee


@router.get("", response_model=list[EmployeeRead], dependencies=[Depends(require_role(*STAFF_ROLES))])
def list_employees(
    skip: int = 0,
    limit: int = 50,
    department_id: int | None = None,
    org_unit_id: int | None = None,
    employment_status: EmploymentStatus | None = None,
    db: Session = Depends(get_db),
) -> list[Employee]:
    return employee_repository.list_employees(
        db, skip=skip, limit=limit, department_id=department_id, org_unit_id=org_unit_id, status_filter=employment_status
    )


@router.post(
    "/import",
    response_model=ImportResult,
    dependencies=[Depends(require_role(Role.ADMIN, Role.HR))],
)
async def import_employees(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    CSV columns: first_name, last_name, email (required), department_id,
    location_id, designation, joining_date (YYYY-MM-DD) — all optional.
    One bad row doesn't block the rest; see import_service for how.
    """
    file_bytes = await file.read()
    result = import_service.import_employees(db, file_bytes, current_user.id)
    db.commit()
    return result


@router.get("/{employee_id}", response_model=EmployeeRead)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_self_or_role("employee_id", *STAFF_ROLES)),
) -> Employee:
    employee = employee_repository.get_by_id(db, employee_id)
    if employee is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")
    return employee


@router.patch(
    "/{employee_id}",
    response_model=EmployeeRead,
    dependencies=[Depends(require_role(Role.ADMIN, Role.HR))],
)
def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Employee:
    employee = employee_repository.get_by_id(db, employee_id)
    if employee is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")

    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    employee = employee_service.update_employee(db, employee, updates, current_user.id)
    db.commit()
    db.refresh(employee)
    return employee


@router.patch(
    "/{employee_id}/status",
    response_model=EmployeeRead,
    dependencies=[Depends(require_role(Role.ADMIN, Role.HR))],
)
def update_employee_status(
    employee_id: int,
    payload: EmployeeStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Employee:
    employee = employee_repository.get_by_id(db, employee_id)
    if employee is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")

    employee = employee_service.change_employment_status(
        db, employee, payload.employment_status, current_user.id
    )
    db.commit()
    db.refresh(employee)
    return employee


@router.get(
    "/{employee_id}/exit-checklist",
    dependencies=[Depends(require_role(Role.ADMIN, Role.HR, Role.IT_SUPPORT))],
)
def get_exit_checklist(employee_id: int, db: Session = Depends(get_db)) -> dict:
    employee = employee_repository.get_by_id(db, employee_id)
    if employee is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")
    return employee_service.get_exit_checklist(db, employee)
