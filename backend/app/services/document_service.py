"""
Document storage service (section 32 of the spec).

Bytes go to local disk under `STORAGE_ROOT/<entity_type>/<entity_id>/`,
named with a UUID prefix to avoid collisions; only the metadata row (see
document_repository) is ever queried by the app. Swapping this for S3/GCS
later means changing `_save_bytes`/`_read_bytes` here — nothing else in
the codebase touches the filesystem directly, so the API and DB schema
don't change.
"""
import uuid
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, status

from app.models.document import Document
from app.models.enums import DocumentEntityType
from app.repositories import document_repository
from app.services import audit_service

STORAGE_ROOT = Path(__file__).resolve().parents[2] / "storage" / "documents"

# Conservative allow-list: enough for the artifacts section 32 names
# (invoices, warranty certificates, handover forms) without opening this
# up to arbitrary executable uploads.
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def save_document(
    db,
    *,
    entity_type: DocumentEntityType,
    entity_id: int,
    doc_type: str,
    file_name: str,
    content_type: Optional[str],
    file_bytes: bytes,
    uploaded_by: int,
) -> Document:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Unsupported file type: {content_type}. Allowed: PDF, Word, Excel, PNG, JPEG.",
        )
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "File exceeds the 10 MB limit.")

    target_dir = STORAGE_ROOT / entity_type.value / str(entity_id)
    target_dir.mkdir(parents=True, exist_ok=True)

    stored_name = f"{uuid.uuid4().hex}_{file_name}"
    target_path = target_dir / stored_name
    target_path.write_bytes(file_bytes)

    document = Document(
        entity_type=entity_type,
        entity_id=entity_id,
        doc_type=doc_type,
        file_name=file_name,
        file_path=str(target_path),
        content_type=content_type,
        uploaded_by=uploaded_by,
    )
    document_repository.create(db, document)

    audit_service.log_action(
        db,
        actor_user_id=uploaded_by,
        action="DOCUMENT_UPLOADED",
        entity_type=entity_type.value,
        entity_id=entity_id,
        new_value={"document_id": document.id, "file_name": file_name, "doc_type": doc_type},
    )
    return document


def read_document_bytes(document: Document) -> bytes:
    path = Path(document.file_path)
    if not path.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Stored file is missing on disk.")
    return path.read_bytes()
