"""Reports router (section 36). Staff roles only; CSV export."""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.database import get_db
from app.core.permissions import Role
from app.services import report_service

router = APIRouter(prefix="/reports", tags=["reports"])

STAFF_ROLES = (Role.ADMIN, Role.HR, Role.IT_SUPPORT)


def _csv_response(content: str, filename: str) -> StreamingResponse:
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/asset-inventory", dependencies=[Depends(require_role(*STAFF_ROLES))])
def asset_inventory_report(db: Session = Depends(get_db)) -> StreamingResponse:
    return _csv_response(report_service.asset_inventory_report(db), "asset-inventory-report.csv")


@router.get("/employee-assets", dependencies=[Depends(require_role(*STAFF_ROLES))])
def employee_asset_report(db: Session = Depends(get_db)) -> StreamingResponse:
    return _csv_response(report_service.employee_asset_report(db), "employee-asset-report.csv")


@router.get("/warranty", dependencies=[Depends(require_role(*STAFF_ROLES))])
def warranty_report(db: Session = Depends(get_db)) -> StreamingResponse:
    return _csv_response(report_service.warranty_report(db), "warranty-report.csv")
