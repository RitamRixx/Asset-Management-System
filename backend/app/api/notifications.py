"""
Notifications router (section 33).

In-app only in this phase (the spec lists email as a later channel).
Every authenticated user sees only their own notifications — there's no
list-all-notifications endpoint even for Admin, since notifications are
inherently personal, not an administrable resource.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.repositories import notification_repository
from app.schemas.notification import NotificationRead

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationRead])
def list_my_notifications(
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Notification]:
    return notification_repository.list_for_user(db, current_user.id, unread_only=unread_only)


@router.post("/{notification_id}/read", response_model=NotificationRead)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Notification:
    notification = notification_repository.get_by_id(db, notification_id)
    if notification is None or notification.recipient_user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")

    notification = notification_repository.mark_read(db, notification)
    db.commit()
    db.refresh(notification)
    return notification
