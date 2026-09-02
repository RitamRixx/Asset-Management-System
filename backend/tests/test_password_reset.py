"""Password reset flow tests (IAM Phase 4)."""
from app.services import password_reset_service


def test_forgot_password_always_returns_202(client):
    response = client.post("/api/v1/auth/forgot-password", json={"email": "nobody@ams-platform-tests.com"})
    assert response.status_code == 202


def test_reset_password_with_valid_token(client, admin, monkeypatch):
    user, _ = admin
    captured = {}
    monkeypatch.setattr(
        password_reset_service.email_service, "send_email",
        lambda *, to, subject, body: captured.setdefault("body", body) or True,
    )
    client.post("/api/v1/auth/forgot-password", json={"email": user.email})
    raw_token = captured["body"].split("token=")[1].strip()

    response = client.post(
        "/api/v1/auth/reset-password", json={"token": raw_token, "new_password": "NewPass456!"}
    )
    assert response.status_code == 200, response.text
    assert response.json()["access_token"]

    old = client.post("/api/v1/auth/login", json={"email": user.email, "password": "AdminPass123!"})
    assert old.status_code == 401
    new = client.post("/api/v1/auth/login", json={"email": user.email, "password": "NewPass456!"})
    assert new.status_code == 200


def test_reset_token_cannot_be_reused(client, admin, monkeypatch):
    user, _ = admin
    captured = {}
    monkeypatch.setattr(
        password_reset_service.email_service, "send_email",
        lambda *, to, subject, body: captured.setdefault("body", body) or True,
    )
    client.post("/api/v1/auth/forgot-password", json={"email": user.email})
    raw_token = captured["body"].split("token=")[1].strip()

    first = client.post("/api/v1/auth/reset-password", json={"token": raw_token, "new_password": "First123!"})
    assert first.status_code == 200

    second = client.post("/api/v1/auth/reset-password", json={"token": raw_token, "new_password": "Second123!"})
    assert second.status_code == 400