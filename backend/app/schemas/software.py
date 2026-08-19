"""
Software/license schemas (sections 17-18).

`LicenseRead.masked_key` is derived from the stored key at read time and
is the *only* representation of the key this API ever returns — there is
no schema anywhere that includes the raw `license_key` column, so "never
expose complete license keys to unauthorized users" holds for every user,
not just unauthorized ones.
"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator

from app.models.enums import LicenseStatus, SoftwareAssignmentStatus


class SoftwareCreate(BaseModel):
    name: str
    publisher: Optional[str] = None
    version: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None


class SoftwareRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    publisher: Optional[str]
    version: Optional[str]
    category: Optional[str]
    description: Optional[str]


class LicenseCreate(BaseModel):
    software_id: int
    license_key: Optional[str] = None
    license_type: Optional[str] = None
    seats: int = 1
    purchase_date: Optional[date] = None
    expiry_date: Optional[date] = None
    vendor_id: Optional[int] = None


class LicenseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    software_id: int
    license_type: Optional[str]
    seats: int
    assigned_seats: int
    purchase_date: Optional[date]
    expiry_date: Optional[date]
    vendor_id: Optional[int]
    status: LicenseStatus
    masked_key: Optional[str] = None

    # Populated from the ORM object's `license_key` in a validator rather
    # than exposed as a field of the same name, so `license_key` itself is
    # never part of this schema's shape.
    @model_validator(mode="before")
    @classmethod
    def _mask_key(cls, obj):
        raw = obj.get("license_key") if isinstance(obj, dict) else getattr(obj, "license_key", None)
        masked = f"****{raw[-4:]}" if raw and len(raw) >= 4 else ("****" if raw else None)

        get = (lambda k: obj.get(k)) if isinstance(obj, dict) else (lambda k: getattr(obj, k, None))
        data = {name: get(name) for name in LicenseRead.model_fields if name != "masked_key"}
        data["masked_key"] = masked
        return data


class SoftwareAssignmentCreate(BaseModel):
    employee_id: int
    license_id: int


class SoftwareAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    employee_id: int
    license_id: int
    assigned_at: datetime
    revoked_at: Optional[datetime]
    status: SoftwareAssignmentStatus
