"""Documents router (section 32). IT/Admin/HR upload; access follows the same
staff-role gate as the rest of the app (no separate per-document ACL in this phase)."""
import io

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.core.permissions import Role
from app.models.document import Document
from app.models.enums import DocumentEntityType
from app.models.user import User
from app.repositories import document_repository
from app.schemas.document import DocumentRead
from app.services import document_service

router = APIRouter(prefix="/documents", tags=["documents"])

STAFF_ROLES = (Role.ADMIN, Role.HR, Role.IT_SUPPORT)
MANAGE_ROLES = (Role.ADMIN, Role.HR, Role.IT_SUPPORT)


@router.post(
    "", response_model=DocumentRead, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(*MANAGE_ROLES))],
)
async def upload_document(
    entity_type: DocumentEntityType = Form(...),
    entity_id: int = Form(...),
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Document:
    file_bytes = await file.read()
    document = document_service.save_document(
        db,
        entity_type=entity_type,
        entity_id=entity_id,
        doc_type=doc_type,
        file_name=file.filename or "upload",
        content_type=file.content_type,
        file_bytes=file_bytes,
        uploaded_by=current_user.id,
    )
    db.commit()
    db.refresh(document)
    return document


@router.get("", response_model=list[DocumentRead], dependencies=[Depends(require_role(*STAFF_ROLES))])
def list_documents(
    entity_type: DocumentEntityType, entity_id: int, db: Session = Depends(get_db)
) -> list[Document]:
    return document_repository.list_for_entity(db, entity_type, entity_id)


@router.get("/{document_id}/download", dependencies=[Depends(require_role(*STAFF_ROLES))])
def download_document(document_id: int, db: Session = Depends(get_db)) -> StreamingResponse:
    document = document_repository.get_by_id(db, document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")

    file_bytes = document_service.read_document_bytes(document)
    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type=document.content_type or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{document.file_name}"'},
    )
