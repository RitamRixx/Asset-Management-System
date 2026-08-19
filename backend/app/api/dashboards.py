"""Dashboards router (section 34)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.core.permissions import Role
from app.models.user import User
from app.repositories import (
    assignment_repository,
    employee_repository,
    repair_repository,
    software_repository,
)
from app.services import dashboard_service

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


@router.get("/admin", dependencies=[Depends(require_role(Role.ADMIN))])
def admin_dashboard(db: Session = Depends(get_db)) -> dict:
    return dashboard_service.admin_dashboard(db)


@router.get("/it", dependencies=[Depends(require_role(Role.ADMIN, Role.IT_SUPPORT))])
def it_dashboard(db: Session = Depends(get_db)) -> dict:
    return dashboard_service.it_dashboard(db)


@router.get("/hr", dependencies=[Depends(require_role(Role.ADMIN, Role.HR))])
def hr_dashboard(db: Session = Depends(get_db)) -> dict:
    return dashboard_service.hr_dashboard(db)


@router.get("/me")
def my_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict:
    """Section 34's Employee dashboard: profile + assets + software + repairs,
    scoped to the logged-in user's own linked Employee record."""
    if current_user.employee_id is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "This account has no linked employee profile.")

    employee = employee_repository.get_by_id(db, current_user.employee_id)
    assignments = assignment_repository.list_for_employee(db, employee.id)
    software = software_repository.list_assignments_for_employee(db, employee.id)
    repairs = repair_repository.list_tickets(db, skip=0, limit=50)
    my_repairs = [r for r in repairs if r.reported_by == employee.id]

    return {
        "employee": {
            "id": employee.id,
            "employee_code": employee.employee_code,
            "full_name": employee.full_name,
            "employment_status": employee.employment_status.value,
        },
        "active_assets": [
            {"asset_id": item.asset_id, "status": item.status.value}
            for a in assignments
            for item in a.items
            if item.status.value == "ACTIVE"
        ],
        "software_count": len(software),
        "open_repair_requests": len([r for r in my_repairs if r.status.value not in ("CLOSED", "CANCELLED", "RESOLVED")]),
    }
