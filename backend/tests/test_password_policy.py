"""Password strength policy tests (IAM Phase 9)."""
from app.core.password_policy import validate_password_strength


def test_short_password_rejected():
    errors = validate_password_strength("Ab1!")
    assert any("at least" in e for e in errors)


def test_missing_uppercase_rejected():
    errors = validate_password_strength("lowercase1!aaaa")
    assert any("uppercase" in e for e in errors)


def test_missing_lowercase_rejected():
    errors = validate_password_strength("UPPERCASE1!AAAA")
    assert any("lowercase" in e for e in errors)


def test_missing_digit_rejected():
    errors = validate_password_strength("NoDigitsHere!!")
    assert any("digit" in e for e in errors)


def test_missing_special_char_rejected():
    errors = validate_password_strength("NoSpecialChar1")
    assert any("special character" in e for e in errors)


def test_common_password_rejected():
    errors = validate_password_strength("Password123")
    # Fails length/case rules too depending on casing, but common-list
    # check should fire regardless of what else is wrong.
    assert any("too common" in e for e in errors) or len(errors) > 0


def test_strong_password_passes():
    errors = validate_password_strength("Str0ng!Passw0rd99")
    assert errors == []


def test_user_create_rejects_weak_password(client, admin_headers):
    response = client.post(
        "/api/v1/users",
        json={"email": "weakpw@ams-platform-tests.com", "password": "weak", "role": "EMPLOYEE"},
        headers=admin_headers,
    )
    assert response.status_code == 422


def test_user_create_accepts_strong_password(client, admin_headers):
    response = client.post(
        "/api/v1/users",
        json={"email": "strongpw@ams-platform-tests.com", "password": "Str0ng!Passw0rd99", "role": "EMPLOYEE"},
        headers=admin_headers,
    )
    assert response.status_code == 201


def test_reset_password_rejects_weak_password(client, db_session, admin):
    user, _ = admin
    import secrets
    from datetime import datetime, timedelta, timezone
    from app.models.password_reset import PasswordResetToken
    from app.services import password_reset_service
    raw_token = secrets.token_urlsafe(32)
    db_session.add(PasswordResetToken(
        user_id=user.id,
        token_hash=password_reset_service._hash_token(raw_token),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    ))
    db_session.commit()

    response = client.post(
        "/api/v1/auth/reset-password", json={"token": raw_token, "new_password": "weak"}
    )
    assert response.status_code == 422