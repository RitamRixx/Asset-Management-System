"""Employee business logic (sections 10, 24)."""
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.assignment import AssignmentItem, AssetAssignment
from app.models.employee import Employee
from app.models.enums import AssignmentStatus, EmploymentStatus, SoftwareAssignmentStatus
from app.models.software import SoftwareAssignment
from app.repositories import employee_repository
from app.services import audit_service
from app.utils.codes import reserve_id_and_code


def create_employee(db: Session, data: dict[str, Any], actor_user_id: int) -> Employee:
    next_id, code = reserve_id_and_code(db, table_name="employees", prefix="EMP")
    employee = Employee(id=next_id, employee_code=code, **data)
    employee_repository.create(db, employee)

    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="EMPLOYEE_CREATED",
        entity_type="Employee",
        entity_id=employee.id,
        new_value={"email": employee.email, "employee_code": employee.employee_code},
    )
    return employee


def update_employee(
    db: Session, employee: Employee, data: dict[str, Any], actor_user_id: int
) -> Employee:
    old_value = {k: getattr(employee, k) for k in data.keys()}
    for key, value in data.items():
        setattr(employee, key, value)
    db.flush()

    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="EMPLOYEE_UPDATED",
        entity_type="Employee",
        entity_id=employee.id,
        old_value={k: str(v) for k, v in old_value.items()},
        new_value={k: str(v) for k, v in data.items()},
    )
    return employee


def change_employment_status(
    db: Session, employee: Employee, new_status: EmploymentStatus, actor_user_id: int
) -> Employee:
    old_status = employee.employment_status
    employee.employment_status = new_status
    db.flush()

    audit_service.log_action(
        db,
        actor_user_id=actor_user_id,
        action="EMPLOYEE_STATUS_CHANGED",
        entity_type="Employee",
        entity_id=employee.id,
        old_value={"employment_status": old_status.value},
        new_value={"employment_status": new_status.value},
    )
    return employee


def get_exit_checklist(db: Session, employee: Employee) -> dict[str, Any]:
    """Section 24: auto-generated asset return checklist + software access
    checklist + clearance status for an employee's exit process."""

    pending_items = list(
        db.scalars(
            select(AssignmentItem)
            .join(AssetAssignment, AssignmentItem.assignment_id == AssetAssignment.id)
            .where(
                AssetAssignment.employee_id == employee.id,
                AssignmentItem.status == AssignmentStatus.ACTIVE,
            )
        )
    )
    pending_software = list(
        db.scalars(
            select(SoftwareAssignment).where(
                SoftwareAssignment.employee_id == employee.id,
                SoftwareAssignment.status == SoftwareAssignmentStatus.ACTIVE,
            )
        )
    )

    return {
        "employee_id": employee.id,
        "pending_asset_returns": [
            {"assignment_item_id": item.id, "asset_id": item.asset_id} for item in pending_items
        ],
        "pending_software_revocations": [
            {"software_assignment_id": sa.id, "license_id": sa.license_id}
            for sa in pending_software
        ],
        "clearance_complete": len(pending_items) == 0 and len(pending_software) == 0,
    }
