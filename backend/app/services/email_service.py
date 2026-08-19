"""
Email delivery (section 33's "later: Email" channel).

Kept deliberately simple — one function, stdlib `smtplib` and `email`,
no third-party mail SDK. When EMAIL_ENABLED is false or SMTP_HOST is
unset (the default), `send_email` logs and returns False instead of
raising, so a deployment with no mail server configured degrades to
in-app-only notifications rather than breaking the request that
triggered them. Errors talking to a *configured* SMTP server are also
caught and logged rather than propagated, for the same reason: a flaky
mail server should never fail the underlying business operation (e.g. an
asset assignment) that happened to also want to send an email about it.
"""
import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger("ams.email")


def send_email(*, to: str, subject: str, body: str) -> bool:
    if not settings.EMAIL_ENABLED or not settings.SMTP_HOST:
        logger.info("Email disabled/unconfigured — skipping send to %s: %s", to, subject)
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    message["To"] = to
    message.set_content(body)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            if settings.SMTP_USERNAME:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(message)
        return True
    except (smtplib.SMTPException, OSError):
        logger.exception("Failed to send email to %s", to)
        return False
