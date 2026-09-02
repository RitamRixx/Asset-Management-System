"""SUSPENDED / PENDING status tests (IAM Phase 7)."""
from app.core.permissions import Role


def test_suspended_user_gets_specific_message(client, admin_headers, it_user):
    user, token = it_user
    client.patch(f"/api/v1/users/{user.id}/status", json={"status": "SUSPENDED"}, headers=admin_headers)

    response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Account is suspended"


def test_pending_user_gets_specific_message(client, admin_headers, it_user):
    user, token = it_user
    client.patch(f"/api/v1/users/{user.id}/status", json={"status": "PENDING"}, headers=admin_headers)

    response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Account is pending activation"


def test_suspended_user_cannot_login(client, admin_headers, it_user):
    user, _ = it_user
    client.patch(f"/api/v1/users/{user.id}/status", json={"status": "SUSPENDED"}, headers=admin_headers)

    login = client.post("/api/v1/auth/login", json={"email": user.email, "password": "ItPass123!"})
    assert login.status_code == 401


def test_status_change_audit_action_matches_status(client, admin_headers, it_user, db_session):
    user, _ = it_user
    client.patch(f"/api/v1/users/{user.id}/status", json={"status": "SUSPENDED"}, headers=admin_headers)

    logs = client.get(
        f"/api/v1/audit-logs?entity_type=User&entity_id={user.id}", headers=admin_headers
    ).json()
    assert any(l["action"] == "USER_SUSPENDED" for l in logs)