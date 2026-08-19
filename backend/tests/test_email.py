"""Email service tests. Doesn't need the DB/client fixtures — send_email
is a pure function of settings + arguments."""
from app.services import email_service


def test_send_email_noop_when_disabled(monkeypatch):
    monkeypatch.setattr(email_service.settings, "EMAIL_ENABLED", False)
    result = email_service.send_email(to="someone@example.com", subject="Test", body="Body")
    assert result is False


def test_send_email_noop_when_no_host_configured(monkeypatch):
    monkeypatch.setattr(email_service.settings, "EMAIL_ENABLED", True)
    monkeypatch.setattr(email_service.settings, "SMTP_HOST", "")
    result = email_service.send_email(to="someone@example.com", subject="Test", body="Body")
    assert result is False


def test_send_email_handles_connection_failure_gracefully(monkeypatch):
    """A configured-but-unreachable SMTP server should return False, not raise —
    a flaky mail server must never fail the business operation that triggered it."""
    monkeypatch.setattr(email_service.settings, "EMAIL_ENABLED", True)
    monkeypatch.setattr(email_service.settings, "SMTP_HOST", "localhost")
    monkeypatch.setattr(email_service.settings, "SMTP_PORT", 1)  # nothing listens here
    result = email_service.send_email(to="someone@example.com", subject="Test", body="Body")
    assert result is False
