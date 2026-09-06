"""hCaptcha verification tests (IAM Phase 10)."""
from unittest.mock import MagicMock, patch

from app.services import captcha_service


def test_login_works_without_captcha_when_disabled(client, admin, monkeypatch):
    monkeypatch.setattr(captcha_service.settings, "HCAPTCHA_ENABLED", False)
    user, _ = admin
    response = client.post(
        "/api/v1/auth/login", json={"email": user.email, "password": "AdminPass123!"}
    )
    assert response.status_code == 200


def test_login_rejects_missing_captcha_token_when_enabled(client, admin, monkeypatch):
    monkeypatch.setattr(captcha_service.settings, "HCAPTCHA_ENABLED", True)
    monkeypatch.setattr(captcha_service.settings, "HCAPTCHA_SECRET_KEY", "fake-secret")
    user, _ = admin
    response = client.post(
        "/api/v1/auth/login", json={"email": user.email, "password": "AdminPass123!"}
    )
    assert response.status_code == 400


def test_login_rejects_failed_captcha_verification(client, admin, monkeypatch):
    monkeypatch.setattr(captcha_service.settings, "HCAPTCHA_ENABLED", True)
    monkeypatch.setattr(captcha_service.settings, "HCAPTCHA_SECRET_KEY", "fake-secret")

    mock_response = MagicMock()
    mock_response.json.return_value = {"success": False}
    with patch("httpx.post", return_value=mock_response):
        user, _ = admin
        response = client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "AdminPass123!", "captcha_token": "bad-token"},
        )
    assert response.status_code == 400


def test_login_succeeds_with_valid_captcha(client, admin, monkeypatch):
    monkeypatch.setattr(captcha_service.settings, "HCAPTCHA_ENABLED", True)
    monkeypatch.setattr(captcha_service.settings, "HCAPTCHA_SECRET_KEY", "fake-secret")

    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True}
    with patch("httpx.post", return_value=mock_response):
        user, _ = admin
        response = client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "AdminPass123!", "captcha_token": "good-token"},
        )
    assert response.status_code == 200


def test_captcha_verification_error_fails_closed(client, admin, monkeypatch):
    """A network error talking to hCaptcha must reject the login, not
    silently let it through — see captcha_service.py's docstring."""
    monkeypatch.setattr(captcha_service.settings, "HCAPTCHA_ENABLED", True)
    monkeypatch.setattr(captcha_service.settings, "HCAPTCHA_SECRET_KEY", "fake-secret")

    import httpx
    with patch("httpx.post", side_effect=httpx.ConnectTimeout("timed out")):
        user, _ = admin
        response = client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "AdminPass123!", "captcha_token": "any-token"},
        )
    assert response.status_code == 503