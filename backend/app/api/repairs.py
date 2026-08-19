"""
Repairs router (sections 25-26).

Employees can raise a ticket on an asset currently assigned to them
(section 6: "Raise repair/service requests"). IT/Admin can raise on behalf
of anyone and drive the ticket through its full status lifecycle.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.core.permissions import Role
from app.models.enums import RepairStatus
from app.models.repair import RepairHistory, RepairTicket
from app.models.user import User
from app.repositories import assignment_repository, asset_repository, repair_repository
from app.schemas.repair import RepairHistoryRead, RepairStatusUpdate, RepairTicketCreate, RepairTicketRead
from app.services import repair_service

router = APIRouter(prefix="/repairs", tags=["repairs"])

STAFF_ROLES = (Role.ADMIN, Role.HR, Role.IT_SUPPORT)
MANAGE_ROLES = (Role.ADMIN, Role.IT_SUPPORT)


@router.post("", response_model=RepairTicketRead, status_code=status.HTTP_201_CREATED)
def create_repair_ticket(
    payload: RepairTicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RepairTicket:
    asset = asset_repository.get_by_id(db, payload.asset_id)
    if asset is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset not found")

    if current_user.role not in STAFF_ROLES:
        # Plain employees may only report issues on their own asset (rule #14's spirit).
        active_item = assignment_repository.get_active_item_for_asset(db, asset.id)
        is_current_holder = (
            active_item is not None
            and active_item.assignment.employee_id == current_user.employee_id
        )
        if not is_current_holder or payload.reported_by != current_user.employee_id:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "You can only raise repair requests for assets currently assigned to you.",
            )

    ticket = repair_service.create_ticket(
        db,
        asset=asset,
        reported_by=payload.reported_by,
        issue=payload.issue,
        priority=payload.priority,
        actor_user_id=current_user.id,
    )
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("", response_model=list[RepairTicketRead], dependencies=[Depends(require_role(*STAFF_ROLES))])
def list_repair_tickets(
    asset_id: int | None = None,
    status_filter: RepairStatus | None = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> list[RepairTicket]:
    return repair_repository.list_tickets(
        db, asset_id=asset_id, status_filter=status_filter, skip=skip, limit=limit
    )


@router.get("/{ticket_id}", response_model=RepairTicketRead, dependencies=[Depends(require_role(*STAFF_ROLES))])
def get_repair_ticket(ticket_id: int, db: Session = Depends(get_db)) -> RepairTicket:
    ticket = repair_repository.get_by_id(db, ticket_id)
    if ticket is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Repair ticket not found")
    return ticket


@router.get(
    "/{ticket_id}/history",
    response_model=list[RepairHistoryRead],
    dependencies=[Depends(require_role(*STAFF_ROLES))],
)
def get_repair_history(ticket_id: int, db: Session = Depends(get_db)) -> list[RepairHistory]:
    return repair_repository.list_history(db, ticket_id)


@router.patch(
    "/{ticket_id}/status",
    response_model=RepairTicketRead,
    dependencies=[Depends(require_role(*MANAGE_ROLES))],
)
def update_repair_status(
    ticket_id: int,
    payload: RepairStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RepairTicket:
    ticket = repair_repository.get_by_id(db, ticket_id)
    if ticket is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Repair ticket not found")

    ticket = repair_service.update_status(
        db,
        ticket=ticket,
        new_status=payload.status,
        diagnosis=payload.diagnosis,
        vendor_id=payload.vendor_id,
        repair_cost=payload.repair_cost,
        repair_start_date=payload.repair_start_date,
        repair_end_date=payload.repair_end_date,
        resolution=payload.resolution,
        notes=payload.notes,
        actor_user_id=current_user.id,
    )
    db.commit()
    db.refresh(ticket)
    return ticket
