"""Document data-access layer (section 32)."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.enums import DocumentEntityType


def get_by_id(db: Session, document_id: int) -> Optional[Document]:
    return db.get(Document, document_id)


def list_for_entity(db: Session, entity_type: DocumentEntityType, entity_id: int) -> list[Document]:
    stmt = (
        select(Document)
        .where(Document.entity_type == entity_type, Document.entity_id == entity_id)
        .order_by(Document.uploaded_at.desc())
    )
    return list(db.scalars(stmt))


def create(db: Session, document: Document) -> Document:
    db.add(document)
    db.flush()
    return document
