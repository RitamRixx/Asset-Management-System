"""Change-password-while-logged-in tests (IAM Phase 9)."""
from app.core.security import verify_password


def test_change_password_success(client, db_session, admin):
    user, token = admin
    response = client.post(
        "/api/v1/users/me/change-password",
        json={"current_password": "AdminPass123!", "new_password": "NewStr0ng!Pass99"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text

    db_session.refresh(user)
    assert verify_password("NewStr0ng!Pass99", user.password_hash)


def test_change_password_wrong_current_password_rejected(client, admin):
    _, token = admin
    response = client.post(
        "/api/v1/users/me/change-password",
        json={"current_password": "totally-wrong", "new_password": "NewStr0ng!Pass99"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


def test_change_password_weak_new_password_rejected(client, admin):
    _, token = admin
    response = client.post(
        "/api/v1/users/me/change-password",
        json={"current_password": "AdminPass123!", "new_password": "weak"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_change_password_requires_auth(client):
    response = client.post(
        "/api/v1/users/me/change-password",
        json={"current_password": "x", "new_password": "NewStr0ng!Pass99"},
    )
    assert response.status_code == 401


def test_changed_password_works_for_next_login(client, admin):
    user, token = admin
    client.post(
        "/api/v1/users/me/change-password",
        json={"current_password": "AdminPass123!", "new_password": "NewStr0ng!Pass99"},
        headers={"Authorization": f"Bearer {token}"},
    )
    login = client.post(
        "/api/v1/auth/login", json={"email": user.email, "password": "NewStr0ng!Pass99"}
    )
    assert login.status_code == 200