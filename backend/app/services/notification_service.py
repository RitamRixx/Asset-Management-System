"""
Notification creation helper (section 33).

Always writes the in-app Notification row. Also attempts an email via
email_service.send_email — a no-op if EMAIL_ENABLED isn't set, so this
function's behavior is identical to before that channel existed unless a
deployment opts in via env vars.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.repositories import user_repository
from app.services import email_service


def notify(
    db: Session,
    *,
    recipient_user_id: int,
    type: str,
    title: str,
    message: str,
    related_entity_type: Optional[str] = None,
    related_entity_id: Optional[int] = None,
) -> Notification:
    n = Notification(
        recipient_user_id=recipient_user_id,
        type=type,
        title=title,
        message=message,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
    )
    db.add(n)
    db.flush()

    recipient = user_repository.get_by_id(db, recipient_user_id)
    if recipient is not None:
        email_service.send_email(to=recipient.email, subject=title, body=message)

    return n

