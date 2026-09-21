"""
Assets router (section 14, plus inventory filters from section 28).

IT/Admin register and edit assets (section 5). HR has read-only visibility
(needed for onboarding/exit checklists). Individual employees see their own
assigned assets via the employee/assignment endpoints, not this list.
"""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.core.permissions import Role
from app.models.asset import Asset
from app.models.enums import AssetStatus
from app.models.user import User
from app.repositories import asset_repository
from app.schemas.asset import AssetCreate, AssetRead, AssetStatusChange, AssetUpdate
from app.schemas.asset_disposal import AssetDisposalCreate, AssetDisposalRead
from app.schemas.service_contract import ServiceContractCreate, ServiceContractRead, ServiceContractUpdate
from app.schemas.import_result import ImportResult
from app.services import asset_service, import_service, asset_disposal_service, service_contract_service

router = APIRouter(prefix="/assets", tags=["assets"])

STAFF_ROLES = (Role.ADMIN, Role.HR, Role.IT_SUPPORT)
MANAGE_ROLES = (Role.ADMIN, Role.IT_SUPPORT)


@router.post(
    "", response_model=AssetRead, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(*MANAGE_ROLES))],
)
def create_asset(
    payload: AssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Asset:
    asset = asset_service.create_asset(db, payload.model_dump(), current_user.id)
    db.commit()
    db.refresh(asset)
    return asset


@router.get("", response_model=list[AssetRead], dependencies=[Depends(require_role(*STAFF_ROLES))])
def list_assets(
    skip: int = 0,
    limit: int = 50,
    asset_type_id: int | None = None,
    location_id: int | None = None,
    org_unit_id: int | None = None,
    status_filter: AssetStatus | None = None,
    manufacturer: str | None = None,
    model: str | None = None,
    vendor_id: int | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
) -> list[Asset]:
    return asset_repository.list_assets(
        db,
        skip=skip,
        limit=limit,
        asset_type_id=asset_type_id,
        location_id=location_id,
        org_unit_id=org_unit_id,
        status_filter=status_filter,
        manufacturer=manufacturer,
        model=model,
        vendor_id=vendor_id,
        q=q,
    )


@router.post(
    "/import",
    response_model=ImportResult,
    dependencies=[Depends(require_role(*MANAGE_ROLES))],
)
async def import_assets(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    CSV columns: asset_type_id (required, numeric), manufacturer, model,
    serial_number, purchase_date (YYYY-MM-DD), purchase_cost, condition
    (NEW/GOOD/FAIR/DAMAGED) — all optional. One bad row doesn't block the rest.
    """
    file_bytes = await file.read()
    result = import_service.import_assets(db, file_bytes, current_user.id)
    db.commit()
    return result


@router.get(
    "/inventory-summary",
    dependencies=[Depends(require_role(*STAFF_ROLES))],
)
def inventory_summary(db: Session = Depends(get_db)) -> dict:
    """Section 28's "Total / Available / Assigned / Under Repair / ..." counts."""
    counts = asset_repository.count_by_status(db)
    return {"total": sum(counts.values()), "by_status": counts}


@router.get("/{asset_id}", response_model=AssetRead, dependencies=[Depends(require_role(*STAFF_ROLES))])
def get_asset(asset_id: int, db: Session = Depends(get_db)) -> Asset:
    asset = asset_repository.get_by_id(db, asset_id)
    if asset is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset not found")
    return asset


@router.patch(
    "/{asset_id}", response_model=AssetRead, dependencies=[Depends(require_role(*MANAGE_ROLES))]
)
def update_asset(
    asset_id: int,
    payload: AssetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Asset:
    asset = asset_repository.get_by_id(db, asset_id)
    if asset is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset not found")

    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    asset = asset_service.update_asset(db, asset, updates, current_user.id)
    db.commit()
    db.refresh(asset)
    return asset


@router.patch(
    "/{asset_id}/status", response_model=AssetRead, dependencies=[Depends(require_role(*MANAGE_ROLES))]
)
def change_asset_status(
    asset_id: int,
    payload: AssetStatusChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Asset:
    asset = asset_repository.get_by_id(db, asset_id)
    if asset is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset not found")

    asset = asset_service.change_status(db, asset, payload.status, payload.notes, current_user.id)
    db.commit()
    db.refresh(asset)
    return asset


@router.post(
    "/{asset_id}/dispose",
    response_model=AssetDisposalRead,
    dependencies=[Depends(require_role(*MANAGE_ROLES))],
)
def dispose_asset(
    asset_id: int,
    payload: AssetDisposalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    asset = asset_repository.get_by_id(db, asset_id)
    if asset is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset not found")

    disposal = asset_disposal_service.dispose_asset(db, asset, payload.model_dump(), current_user.id)
    db.commit()
    db.refresh(disposal)
    return disposal


@router.get(
    "/{asset_id}/contracts",
    response_model=list[ServiceContractRead],
    dependencies=[Depends(require_role(*STAFF_ROLES))],
)
def list_contracts(
    asset_id: int,
    db: Session = Depends(get_db),
):
    asset = asset_repository.get_by_id(db, asset_id)
    if asset is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset not found")
        
    return service_contract_service.list_contracts_for_asset(db, asset_id)


@router.post(
    "/{asset_id}/contracts",
    response_model=ServiceContractRead,
    dependencies=[Depends(require_role(*MANAGE_ROLES))],
)
def create_contract(
    asset_id: int,
    payload: ServiceContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    asset = asset_repository.get_by_id(db, asset_id)
    if asset is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asset not found")
        
    contract = service_contract_service.create_contract(db, asset_id, payload.model_dump(), current_user.id)
    db.commit()
    db.refresh(contract)
    return contract


@router.patch(
    "/{asset_id}/contracts/{contract_id}",
    response_model=ServiceContractRead,
    dependencies=[Depends(require_role(*MANAGE_ROLES))],
)
def update_contract(
    asset_id: int,
    contract_id: int,
    payload: ServiceContractUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.service_contract import ServiceContract
    contract = db.get(ServiceContract, contract_id)
    if contract is None or contract.asset_id != asset_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Service contract not found")
        
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    contract = service_contract_service.update_contract(db, contract, updates, current_user.id)
    db.commit()
    db.refresh(contract)
    return contract
