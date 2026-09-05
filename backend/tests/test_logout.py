"""Logout / token revocation tests (IAM Phase 9)."""


def test_logout_revokes_current_token(client, admin):
    _, token = admin
    headers = {"Authorization": f"Bearer {token}"}

    logout = client.post("/api/v1/auth/logout", headers=headers)
    assert logout.status_code == 200

    # Same token should now be rejected everywhere.
    me = client.get("/api/v1/users/me", headers=headers)
    assert me.status_code == 401


def test_logout_requires_auth(client):
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 401


def test_different_users_tokens_are_independent(client, admin, it_user):
    _, admin_token = admin
    _, it_token = it_user

    client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {admin_token}"})

    # IT's token is unaffected by admin's logout.
    still_valid = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {it_token}"}
    )
    assert still_valid.status_code == 200


def test_logging_in_again_after_logout_issues_a_working_token(client, admin):
    user, token = admin
    client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})

    relogin = client.post(
        "/api/v1/auth/login", json={"email": user.email, "password": "AdminPass123!"}
    )
    assert relogin.status_code == 200
    new_token = relogin.json()["access_token"]

    me = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {new_token}"})
    assert me.status_code == 200