"""Reference/config data schemas (sections 11-13)."""
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DepartmentCreate(BaseModel):
    name: str
    code: Optional[str] = None
    manager_id: Optional[int] = None


class DepartmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    code: Optional[str]
    manager_id: Optional[int]
    status: str


class OrgUnitTypeCreate(BaseModel):
    name: str
    code: Optional[str] = None
    typical_rank: Optional[int] = None


class OrgUnitTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    code: Optional[str]
    typical_rank: Optional[int]
    status: str


class OrgUnitCreate(BaseModel):
    name: str
    code: Optional[str] = None
    unit_type_id: int
    parent_id: Optional[int] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    manager_id: Optional[int] = None


class OrgUnitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    code: Optional[str]
    unit_type_id: int
    parent_id: Optional[int]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    manager_id: Optional[int]
    status: str



class LocationCreate(BaseModel):
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None


class LocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    status: str


class VendorCreate(BaseModel):
    name: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None


class VendorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    contact_email: Optional[str]
    contact_phone: Optional[str]
    address: Optional[str]
    status: str


class AssetCategoryCreate(BaseModel):
    name: str

class AssetCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    status: str

class SoftwareCategoryCreate(BaseModel):
    name: str

class SoftwareCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    status: str

class AssetTypeCreate(BaseModel):
    name: str
    code: Optional[str] = None
    category_id: Optional[int] = None


class AssetTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    code: Optional[str]
    category_id: Optional[int]
    status: str


class ComponentTypeCreate(BaseModel):
    name: str


class ComponentTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    status: str
