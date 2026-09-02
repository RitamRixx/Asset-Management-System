"""Organization settings tests (IAM Phase 8)."""


def test_get_organization_returns_defaults_when_unset(client, it_headers):
    response = client.get("/api/v1/organization", headers=it_headers)
    assert response.status_code == 200
    assert response.json()["company_name"] == "AMS Platform"


def test_admin_can_update_organization(client, admin_headers):
    response = client.patch(
        "/api/v1/organization",
        json={"company_name": "Logarhythm", "tagline": "We make it work for you"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["company_name"] == "Logarhythm"


def test_non_admin_cannot_update_organization(client, it_headers):
    response = client.patch("/api/v1/organization", json={"company_name": "Hijacked"}, headers=it_headers)
    assert response.status_code == 403


def test_settings_persist_across_requests(client, admin_headers, it_headers):
    client.patch("/api/v1/organization", json={"tagline": "Persisted Tagline"}, headers=admin_headers)
    response = client.get("/api/v1/organization", headers=it_headers)
    assert response.json()["tagline"] == "Persisted Tagline"