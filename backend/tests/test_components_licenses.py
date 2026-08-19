"""Component replacement (section 16) and license seat-limit (rule #11) tests."""


def test_component_replacement_preserves_history(client, it_headers, sample_asset, sample_component_type):
    install = client.post(
        f"/api/v1/assets/{sample_asset['id']}/components",
        json={"component_type_id": sample_component_type["id"], "description": "8 GB RAM"},
        headers=it_headers,
    )
    assert install.status_code == 201
    old_component = install.json()

    replace = client.post(
        f"/api/v1/components/{old_component['id']}/replace",
        json={"description": "16 GB RAM"},
        headers=it_headers,
    )
    assert replace.status_code == 200
    new_component = replace.json()

    history = client.get(
        f"/api/v1/assets/{sample_asset['id']}/components", headers=it_headers
    ).json()
    by_id = {c["id"]: c for c in history}

    assert by_id[old_component["id"]]["status"] == "REMOVED"
    assert by_id[old_component["id"]]["replaced_by_component_id"] == new_component["id"]
    assert by_id[new_component["id"]]["status"] == "ACTIVE"


def test_cannot_replace_an_already_removed_component(client, it_headers, sample_asset, sample_component_type):
    install = client.post(
        f"/api/v1/assets/{sample_asset['id']}/components",
        json={"component_type_id": sample_component_type["id"], "description": "8 GB RAM"},
        headers=it_headers,
    ).json()
    client.post(
        f"/api/v1/components/{install['id']}/replace",
        json={"description": "16 GB RAM"},
        headers=it_headers,
    )

    second_replace = client.post(
        f"/api/v1/components/{install['id']}/replace",
        json={"description": "32 GB RAM"},
        headers=it_headers,
    )
    assert second_replace.status_code == 409


def test_license_seat_limit_enforced(client, it_headers, admin_headers, sample_employee):
    software = client.post(
        "/api/v1/software", json={"name": "Test Suite Pro"}, headers=it_headers
    ).json()
    license_ = client.post(
        "/api/v1/licenses",
        json={"software_id": software["id"], "seats": 1},
        headers=it_headers,
    ).json()

    first = client.post(
        "/api/v1/software-assignments",
        json={"employee_id": sample_employee["id"], "license_id": license_["id"]},
        headers=it_headers,
    )
    assert first.status_code == 201

    second_employee = client.post(
        "/api/v1/employees",
        json={"first_name": "Second", "last_name": "User", "email": "second.user@ams-platform-tests.com"},
        headers=admin_headers,
    ).json()
    second = client.post(
        "/api/v1/software-assignments",
        json={"employee_id": second_employee["id"], "license_id": license_["id"]},
        headers=it_headers,
    )
    assert second.status_code == 409


def test_expired_license_cannot_be_assigned(client, it_headers, sample_employee):
    software = client.post(
        "/api/v1/software", json={"name": "Old Software"}, headers=it_headers
    ).json()
    license_ = client.post(
        "/api/v1/licenses",
        json={"software_id": software["id"], "seats": 10, "expiry_date": "2020-01-01"},
        headers=it_headers,
    ).json()

    response = client.post(
        "/api/v1/software-assignments",
        json={"employee_id": sample_employee["id"], "license_id": license_["id"]},
        headers=it_headers,
    )
    assert response.status_code == 409


def test_license_key_never_exposed_raw(client, it_headers):
    software = client.post(
        "/api/v1/software", json={"name": "Secret Software"}, headers=it_headers
    ).json()
    response = client.post(
        "/api/v1/licenses",
        json={"software_id": software["id"], "seats": 1, "license_key": "SUPER-SECRET-KEY-9999"},
        headers=it_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert "license_key" not in body
    assert body["masked_key"] == "****9999"
