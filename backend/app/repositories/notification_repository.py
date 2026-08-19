"""Notification data-access layer (section 33)."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification import Notification


def get_by_id(db: Session, notification_id: int) -> Optional[Notification]:
    return db.get(Notification, notification_id)


def list_for_user(db: Session, user_id: int, unread_only: bool = False) -> list[Notification]:
    stmt = select(Notification).where(Notification.recipient_user_id == user_id)
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))
    stmt = stmt.order_by(Notification.created_at.desc())
    return list(db.scalars(stmt))


def mark_read(db: Session, notification: Notification) -> Notification:
    notification.is_read = True
    db.flush()
    return notification
