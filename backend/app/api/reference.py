"""
Reference/config data endpoints (sections 11-13): Departments, Locations,
Vendors, AssetTypes, ComponentTypes.

Admin manages these (section 3: "Manage departments / locations / asset
types"); any authenticated staff role can list them (needed to populate
dropdowns on the Employee/Asset forms).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.database import get_db
from app.core.permissions import Role
from app.models.asset_type import AssetType, ComponentType
from app.models.org import Department, Location, Vendor
from app.schemas.reference import (
    AssetTypeCreate,
    AssetTypeRead,
    ComponentTypeCreate,
    ComponentTypeRead,
    DepartmentCreate,
    DepartmentRead,
    LocationCreate,
    LocationRead,
    VendorCreate,
    VendorRead,
)

router = APIRouter(tags=["reference-data"])

STAFF_ROLES = (Role.ADMIN, Role.HR, Role.IT_SUPPORT)


def _register_lookup_crud(prefix: str, model, create_schema, read_schema):
    sub = APIRouter(prefix=prefix)

    @sub.post(
        "", response_model=read_schema, status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(require_role(Role.ADMIN))],
    )
    def create(payload: create_schema, db: Session = Depends(get_db)):  # type: ignore[valid-type]
        row = model(**payload.model_dump())
        db.add(row)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"'{payload.name}' already exists.",
            )
        db.refresh(row)
        return row

    @sub.get("", response_model=list[read_schema], dependencies=[Depends(require_role(*STAFF_ROLES))])
    def list_rows(db: Session = Depends(get_db)):
        return list(db.scalars(select(model)))

    router.include_router(sub)


_register_lookup_crud("/departments", Department, DepartmentCreate, DepartmentRead)
_register_lookup_crud("/locations", Location, LocationCreate, LocationRead)
_register_lookup_crud("/vendors", Vendor, VendorCreate, VendorRead)
_register_lookup_crud("/asset-types", AssetType, AssetTypeCreate, AssetTypeRead)
_register_lookup_crud("/component-types", ComponentType, ComponentTypeCreate, ComponentTypeRead)
