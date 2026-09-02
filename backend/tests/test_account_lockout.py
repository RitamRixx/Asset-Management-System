"""Account lockout tests (IAM Phase 4)."""
from app.core.config import settings


def test_account_locks_after_threshold_failed_attempts(client, admin):
    user, _ = admin
    for _ in range(settings.LOGIN_LOCKOUT_THRESHOLD):
        client.post("/api/v1/auth/login", json={"email": user.email, "password": "wrong"})

    response = client.post("/api/v1/auth/login", json={"email": user.email, "password": "AdminPass123!"})
    assert response.status_code == 401  # correct password rejected — locked out


def test_successful_login_resets_failed_count(client, admin, db_session):
    user, _ = admin
    client.post("/api/v1/auth/login", json={"email": user.email, "password": "wrong"})
    client.post("/api/v1/auth/login", json={"email": user.email, "password": "AdminPass123!"})

    db_session.refresh(user)
    assert user.failed_login_count == 0
    assert user.locked_until is None