"""Entra SSO tests (IAM Phase 3). msal's ConfidentialClientApplication is
mocked throughout — there's no live Azure AD reachable from this sandbox,
and these tests are about our own logic (tenant check, no-self-signup,
account linking), not Microsoft's implementation of OIDC."""
from unittest.mock import MagicMock

from app.services import entra_service

from app.core.security import create_sso_state_token


def test_sso_login_404_when_disabled(client, monkeypatch):
    monkeypatch.setattr(entra_service.settings, "ENTRA_ENABLED", False)
    response = client.get("/api/v1/auth/sso/login")
    assert response.status_code == 404


def test_sso_login_returns_authorization_url_when_enabled(client, monkeypatch):
    monkeypatch.setattr(entra_service.settings, "ENTRA_ENABLED", True)
    monkeypatch.setattr(entra_service.settings, "ENTRA_TENANT_ID", "test-tenant")
    monkeypatch.setattr(entra_service.settings, "ENTRA_CLIENT_ID", "test-client")
    monkeypatch.setattr(entra_service.settings, "ENTRA_REDIRECT_URI", "http://localhost:3000/sso/callback")

    fake_app = MagicMock()
    fake_app.get_authorization_request_url.return_value = "https://login.microsoftonline.com/fake"
    monkeypatch.setattr(entra_service, "_msal_app", lambda: fake_app)

    response = client.get("/api/v1/auth/sso/login")
    assert response.status_code == 200
    assert response.json()["authorization_url"] == "https://login.microsoftonline.com/fake"


def _enable_entra(monkeypatch, allowed_tenant: str = ""):
    monkeypatch.setattr(entra_service.settings, "ENTRA_ENABLED", True)
    monkeypatch.setattr(entra_service.settings, "ENTRA_TENANT_ID", "test-tenant")
    monkeypatch.setattr(entra_service.settings, "ENTRA_CLIENT_ID", "test-client")
    monkeypatch.setattr(entra_service.settings, "ENTRA_REDIRECT_URI", "http://localhost:3000/sso/callback")
    monkeypatch.setattr(entra_service.settings, "ENTRA_ALLOWED_TENANT_ID", allowed_tenant)


def _mock_successful_exchange(monkeypatch, claims: dict):
    fake_app = MagicMock()
    fake_app.acquire_token_by_authorization_code.return_value = {"id_token_claims": claims}
    monkeypatch.setattr(entra_service, "_msal_app", lambda: fake_app)


def test_callback_rejects_unknown_email(client, db_session, monkeypatch):
    _enable_entra(monkeypatch)
    _mock_successful_exchange(
        monkeypatch,
        {"oid": "obj-1", "tid": "test-tenant", "preferred_username": "nobody@ams-platform-tests.com"},
    )
    # state = entra_service.create_sso_state_token({"code_verifier": "v", "nonce": "n"})
    state = create_sso_state_token({"code_verifier": "v", "nonce": "n"})


    response = client.get(f"/api/v1/auth/sso/callback?code=fake-code&state={state}")
    assert response.status_code == 403
    assert "No AMS account" in response.json()["detail"]


def test_callback_links_existing_local_account(client, db_session, admin, monkeypatch):
    user, _ = admin
    _enable_entra(monkeypatch)
    _mock_successful_exchange(
        monkeypatch,
        {"oid": "obj-admin-1", "tid": "test-tenant", "preferred_username": user.email},
    )
    # state = entra_service.create_sso_state_token({"code_verifier": "v", "nonce": "n"})
    state = create_sso_state_token({"code_verifier": "v", "nonce": "n"})


    response = client.get(f"/api/v1/auth/sso/callback?code=fake-code&state={state}")
    assert response.status_code == 200, response.text
    assert response.json()["access_token"]

    db_session.refresh(user)
    assert user.auth_provider.value == "MICROSOFT"
    assert user.entra_object_id == "obj-admin-1"


def test_callback_rejects_wrong_tenant(client, db_session, admin, monkeypatch):
    user, _ = admin
    _enable_entra(monkeypatch, allowed_tenant="only-this-tenant")
    _mock_successful_exchange(
        monkeypatch,
        {"oid": "obj-admin-2", "tid": "some-other-tenant", "preferred_username": user.email},
    )
    # state = entra_service.create_sso_state_token({"code_verifier": "v", "nonce": "n"})
    state = create_sso_state_token({"code_verifier": "v", "nonce": "n"})


    response = client.get(f"/api/v1/auth/sso/callback?code=fake-code&state={state}")
    assert response.status_code == 403


def test_callback_rejects_invalid_state(client, db_session, monkeypatch):
    _enable_entra(monkeypatch)
    response = client.get("/api/v1/auth/sso/callback?code=fake-code&state=garbage")
    assert response.status_code == 400