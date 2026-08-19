"""
Document metadata model (section 32 of the spec).

Only metadata lives in Postgres, per the spec's own instruction not to
store large files directly in DB rows. `file_path` points at wherever the
bytes actually live — local disk in this Phase 18 implementation (see
services/document_service.py), swappable for S3/GCS later without a schema
change.

`entity_type` + `entity_id` is a simple polymorphic association so one
table can attach documents to employees, assets, repairs, warranties, or
assignments (section 32's list) without a join table per entity type.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import DocumentEntityType


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[DocumentEntityType] = mapped_column(nullable=False)
    entity_id: Mapped[int] = mapped_column(nullable=False)

    doc_type: Mapped[str] = mapped_column(String(50), nullable=False)  # INVOICE, WARRANTY_CERTIFICATE, ...
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[Optional[str]] = mapped_column(String(100))

    uploaded_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
