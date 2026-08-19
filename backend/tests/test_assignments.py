"""Asset assignment business rule tests (business rules #1-4, #7; section 50)."""


def test_duplicate_serial_number_rejected(client, it_headers, sample_asset_type):
    payload = {"asset_type_id": sample_asset_type["id"], "serial_number": "DUPLICATE-SN-1"}
    first = client.post("/api/v1/assets", json=payload, headers=it_headers)
    assert first.status_code == 201

    second = client.post("/api/v1/assets", json=payload, headers=it_headers)
    assert second.status_code == 409


def test_it_can_assign_available_asset(client, it_headers, sample_asset, sample_employee):
    response = client.post(
        "/api/v1/assignments",
        json={"employee_id": sample_employee["id"], "items": [{"asset_id": sample_asset["id"]}]},
        headers=it_headers,
    )
    assert response.status_code == 201
    asset_after = client.get(f"/api/v1/assets/{sample_asset['id']}", headers=it_headers).json()
    assert asset_after["status"] == "ASSIGNED"


def test_cannot_assign_lost_asset(client, it_headers, sample_asset, sample_employee):
    """Business rule #1: an asset marked LOST cannot be assigned."""
    client.patch(f"/api/v1/assets/{sample_asset['id']}/status", json={"status": "LOST"}, headers=it_headers)

    response = client.post(
        "/api/v1/assignments",
        json={"employee_id": sample_employee["id"], "items": [{"asset_id": sample_asset["id"]}]},
        headers=it_headers,
    )
    assert response.status_code == 409


def test_cannot_assign_retired_asset(client, it_headers, sample_asset, sample_employee):
    """Business rule #2."""
    client.patch(f"/api/v1/assets/{sample_asset['id']}/status", json={"status": "RETIRED"}, headers=it_headers)

    response = client.post(
        "/api/v1/assignments",
        json={"employee_id": sample_employee["id"], "items": [{"asset_id": sample_asset["id"]}]},
        headers=it_headers,
    )
    assert response.status_code == 409


def test_cannot_double_assign_asset(client, it_headers, sample_asset, sample_employee):
    """Business rule #4: an asset can have only one active assignment at a time."""
    client.post(
        "/api/v1/assignments",
        json={"employee_id": sample_employee["id"], "items": [{"asset_id": sample_asset["id"]}]},
        headers=it_headers,
    )
    response = client.post(
        "/api/v1/assignments",
        json={"employee_id": sample_employee["id"], "items": [{"asset_id": sample_asset["id"]}]},
        headers=it_headers,
    )
    assert response.status_code == 409


def test_returned_asset_cannot_be_returned_again(client, it_headers, sample_asset, sample_employee):
    """Section 50: 'A returned asset cannot have an active assignment.'"""
    assignment = client.post(
        "/api/v1/assignments",
        json={"employee_id": sample_employee["id"], "items": [{"asset_id": sample_asset["id"]}]},
        headers=it_headers,
    ).json()
    item_id = assignment["items"][0]["id"]

    first_return = client.post(
        "/api/v1/returns",
        json={"assignment_item_id": item_id, "return_condition": "GOOD"},
        headers=it_headers,
    )
    assert first_return.status_code == 201

    second_return = client.post(
        "/api/v1/returns",
        json={"assignment_item_id": item_id, "return_condition": "GOOD"},
        headers=it_headers,
    )
    assert second_return.status_code == 409


def test_return_frees_asset_back_to_available(client, it_headers, sample_asset, sample_employee):
    assignment = client.post(
        "/api/v1/assignments",
        json={"employee_id": sample_employee["id"], "items": [{"asset_id": sample_asset["id"]}]},
        headers=it_headers,
    ).json()
    item_id = assignment["items"][0]["id"]

    client.post(
        "/api/v1/returns",
        json={"assignment_item_id": item_id, "return_condition": "GOOD"},
        headers=it_headers,
    )
    asset_after = client.get(f"/api/v1/assets/{sample_asset['id']}", headers=it_headers).json()
    assert asset_after["status"] == "AVAILABLE"


def test_missing_return_marks_asset_lost(client, it_headers, sample_asset, sample_employee):
    assignment = client.post(
        "/api/v1/assignments",
        json={"employee_id": sample_employee["id"], "items": [{"asset_id": sample_asset["id"]}]},
        headers=it_headers,
    ).json()
    item_id = assignment["items"][0]["id"]

    client.post(
        "/api/v1/returns",
        json={"assignment_item_id": item_id, "return_condition": "MISSING"},
        headers=it_headers,
    )
    asset_after = client.get(f"/api/v1/assets/{sample_asset['id']}", headers=it_headers).json()
    assert asset_after["status"] == "LOST"


def test_cannot_set_status_to_assigned_directly(client, it_headers, sample_asset):
    """ASSIGNED is workflow-only, not a manually settable status."""
    response = client.patch(
        f"/api/v1/assets/{sample_asset['id']}/status", json={"status": "ASSIGNED"}, headers=it_headers
    )
    assert response.status_code == 400
