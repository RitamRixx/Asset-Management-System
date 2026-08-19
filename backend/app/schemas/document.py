"""Document metadata schemas (section 32)."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import DocumentEntityType


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_type: DocumentEntityType
    entity_id: int
    doc_type: str
    file_name: str
    content_type: Optional[str]
    uploaded_by: Optional[int]
    uploaded_at: datetime
