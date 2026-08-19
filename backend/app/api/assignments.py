"""Assignments router (sections 19-21)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role, require_self_or_role
from app.core.database import get_db
from app.core.permissions import Role
from app.models.assignment import AssetAssignment
from app.models.user import User
from app.repositories import assignment_repository
from app.schemas.assignment import AssignmentCreate, AssignmentRead, CurrentAssignmentRead
from app.services import assignment_service

router = APIRouter(tags=["assignments"])

STAFF_ROLES = (Role.ADMIN, Role.HR, Role.IT_SUPPORT)
MANAGE_ROLES = (Role.ADMIN, Role.IT_SUPPORT)


@router.get(
    "/assets/{asset_id}/current-assignment",
    response_model=CurrentAssignmentRead | None,
    dependencies=[Depends(require_role(*STAFF_ROLES))],
)
def get_current_assignment(asset_id: int, db: Session = Depends(get_db)):
    item = assignment_repository.get_active_item_for_asset(db, asset_id)
    if item is None:
        return None
    return CurrentAssignmentRead(
        assignment_item_id=item.id,
        assignment_id=item.assignment_id,
        asset_id=item.asset_id,
        employee_id=item.assignment.employee_id,
        assigned_at=item.assignment.assigned_at,
    )


@router.post(
    "/assignments", response_model=AssignmentRead, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(*MANAGE_ROLES))],
)
def create_assignment(
    payload: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssetAssignment:
    data = payload.model_dump()
    assignment = assignment_service.create_assignment(db, data, current_user.id)
    db.commit()
    return assignment_repository.get_by_id(db, assignment.id)


@router.get(
    "/assignments/{assignment_id}",
    response_model=AssignmentRead,
    dependencies=[Depends(require_role(*STAFF_ROLES))],
)
def get_assignment(assignment_id: int, db: Session = Depends(get_db)) -> AssetAssignment:
    assignment = assignment_repository.get_by_id(db, assignment_id)
    if assignment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Assignment not found")
    return assignment


@router.get(
    "/employees/{employee_id}/assignments",
    response_model=list[AssignmentRead],
)
def list_employee_assignments(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_self_or_role("employee_id", *STAFF_ROLES)),
) -> list[AssetAssignment]:
    return assignment_repository.list_for_employee(db, employee_id)


@router.post("/assignments/{assignment_id}/acknowledge", response_model=AssignmentRead)
def acknowledge_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssetAssignment:
    assignment = assignment_repository.get_by_id(db, assignment_id)
    if assignment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Assignment not found")

    is_owner = current_user.employee_id == assignment.employee_id
    is_staff = current_user.role in STAFF_ROLES
    if not (is_owner or is_staff):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only acknowledge your own handovers")

    assignment_service.acknowledge_assignment(db, assignment, current_user.id)
    db.commit()
    return assignment_repository.get_by_id(db, assignment.id)
