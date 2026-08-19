"""AssetComponent schemas (sections 15-16)."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import ComponentStatus


class ComponentInstall(BaseModel):
    component_type_id: int
    description: str
    serial_number: Optional[str] = None


class ComponentReplace(BaseModel):
    """Describes the new component going in; the old one is looked up by id
    in the path and closed out automatically."""

    description: str
    serial_number: Optional[str] = None


class ComponentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_id: int
    component_type_id: int
    description: str
    serial_number: Optional[str]
    status: ComponentStatus
    installed_at: datetime
    removed_at: Optional[datetime]
    replaced_by_component_id: Optional[int]
