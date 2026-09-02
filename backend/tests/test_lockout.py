"""Account lockout tests (IAM Phase 5)."""
from app.core.config import settings


def test_account_locks_after_max_failed_attempts(client, admin):
    user, _ = admin
    for _ in range(settings.MAX_FAILED_LOGIN_ATTEMPTS):
        response = client.post("/api/v1/auth/login", json={"email": user.email, "password": "wrong"})
        assert response.status_code == 401

    # Correct password no longer works once locked.
    locked_attempt = client.post(
        "/api/v1/auth/login", json={"email": user.email, "password": "AdminPass123!"}
    )
    assert locked_attempt.status_code == 401


def test_successful_login_resets_failed_count(client, db_session, admin):
    user, _ = admin
    client.post("/api/v1/auth/login", json={"email": user.email, "password": "wrong"})
    client.post("/api/v1/auth/login", json={"email": user.email, "password": "wrong"})

    good = client.post("/api/v1/auth/login", json={"email": user.email, "password": "AdminPass123!"})
    assert good.status_code == 200

    db_session.refresh(user)
    assert user.failed_login_count == 0
    assert user.locked_until is None


def test_password_reset_clears_lockout(client, db_session, admin):
    """Regression guard: Phase 4's reset_password must actually clear the
    fields Phase 5 introduced, or a locked-out user could reset their
    password and still be unable to log in."""
    user, _ = admin
    from app.core.config import settings as s
    for _ in range(s.MAX_FAILED_LOGIN_ATTEMPTS):
        client.post("/api/v1/auth/login", json={"email": user.email, "password": "wrong"})

    db_session.refresh(user)
    assert user.locked_until is not None

    from app.services import password_reset_service
    import secrets
    from datetime import datetime, timedelta, timezone
    from app.models.password_reset import PasswordResetToken
    raw_token = secrets.token_urlsafe(32)
    db_session.add(PasswordResetToken(
        user_id=user.id,
        token_hash=password_reset_service._hash_token(raw_token),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    ))
    db_session.commit()

    client.post("/api/v1/auth/reset-password", json={"token": raw_token, "new_password": "Recovered123!"})

    good = client.post("/api/v1/auth/login", json={"email": user.email, "password": "Recovered123!"})
    assert good.status_code == 200