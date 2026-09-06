"""Mid-session revocation tests (IAM Phase 10)."""


def test_disabling_user_revokes_their_active_token(client, admin_headers, it_user):
    user, token = it_user
    headers = {"Authorization": f"Bearer {token}"}

    # Token works before disable.
    assert client.get("/api/v1/users/me", headers=headers).status_code == 200

    disable = client.patch(
        f"/api/v1/users/{user.id}/status", json={"status": "DISABLED"}, headers=admin_headers
    )
    assert disable.status_code == 200

    # Same token is now dead, immediately — not just at next natural expiry.
    after = client.get("/api/v1/users/me", headers=headers)
    assert after.status_code in (401, 403)


def test_suspending_user_revokes_multiple_active_tokens(client, admin_headers, db_session):
    from app.core.permissions import Role
    from app.core.security import hash_password
    from app.models.enums import UserStatus
    from app.models.user import User

    user = User(
        email="multisession@ams-platform-tests.com",
        password_hash=hash_password("MultiSession1!"),
        role=Role.IT_SUPPORT,
        status=UserStatus.ACTIVE,
    )
    db_session.add(user)
    db_session.commit()

    # Two separate "device" logins for the same user.
    login_a = client.post(
        "/api/v1/auth/login", json={"email": user.email, "password": "MultiSession1!"}
    ).json()["access_token"]
    login_b = client.post(
        "/api/v1/auth/login", json={"email": user.email, "password": "MultiSession1!"}
    ).json()["access_token"]

    client.patch(
        f"/api/v1/users/{user.id}/status", json={"status": "SUSPENDED"}, headers=admin_headers
    )

    assert client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {login_a}"}).status_code == 403
    assert client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {login_b}"}).status_code == 403


def test_reactivating_user_does_not_revoke_new_tokens(client, admin_headers, it_user):
    user, _ = it_user
    client.patch(f"/api/v1/users/{user.id}/status", json={"status": "DISABLED"}, headers=admin_headers)
    client.patch(f"/api/v1/users/{user.id}/status", json={"status": "ACTIVE"}, headers=admin_headers)

    relogin = client.post(
        "/api/v1/auth/login", json={"email": user.email, "password": "ItPass123!"}
    )
    assert relogin.status_code == 200
    new_token = relogin.json()["access_token"]

    me = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {new_token}"})
    assert me.status_code == 200


def test_change_password_revokes_other_sessions_but_not_current_one(client, db_session):
    from app.core.permissions import Role
    from app.core.security import hash_password
    from app.models.enums import UserStatus
    from app.models.user import User

    user = User(
        email="selfrevoke@ams-platform-tests.com",
        password_hash=hash_password("OldPass123!!"),
        role=Role.IT_SUPPORT,
        status=UserStatus.ACTIVE,
    )
    db_session.add(user)
    db_session.commit()

    device_a = client.post(
        "/api/v1/auth/login", json={"email": user.email, "password": "OldPass123!!"}
    ).json()["access_token"]
    device_b = client.post(
        "/api/v1/auth/login", json={"email": user.email, "password": "OldPass123!!"}
    ).json()["access_token"]

    # device_a changes the password.
    change = client.post(
        "/api/v1/users/me/change-password",
        json={"current_password": "OldPass123!!", "new_password": "NewStr0ng!Pass99"},
        headers={"Authorization": f"Bearer {device_a}"},
    )
    assert change.status_code == 200

    # device_a's own token still works (the request that triggered the
    # change isn't self-revoked).
    still_a = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {device_a}"})
    assert still_a.status_code == 200

    # device_b is kicked out.
    dead_b = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {device_b}"})
    assert dead_b.status_code == 401


def test_disable_with_no_active_sessions_does_not_error(client, admin_headers, sample_employee):
    """A user who's never logged in (or whose token already expired) has
    zero IssuedToken rows — revoke_all_for_user must handle an empty list
    cleanly rather than assuming at least one exists."""
    from app.core.permissions import Role
    create = client.post(
        "/api/v1/users",
        json={"email": "neverloggedin@ams-platform-tests.com", "password": "Str0ng!Passw0rd99", "role": "EMPLOYEE"},
        headers=admin_headers,
    )
    user_id = create.json()["id"]

    response = client.patch(
        f"/api/v1/users/{user_id}/status", json={"status": "DISABLED"}, headers=admin_headers
    )
    assert response.status_code == 200