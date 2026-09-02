"""Group CRUD tests (IAM Phase 6)."""


def test_admin_can_create_group(client, admin_headers):
    response = client.post("/api/v1/groups", json={"name": "Sales Ops"}, headers=admin_headers)
    assert response.status_code == 201, response.text
    assert response.json()["status"] == "ACTIVE"


def test_duplicate_group_name_returns_409(client, admin_headers):
    client.post("/api/v1/groups", json={"name": "Duplicate Group"}, headers=admin_headers)
    second = client.post("/api/v1/groups", json={"name": "Duplicate Group"}, headers=admin_headers)
    assert second.status_code == 409


def test_it_cannot_create_group(client, it_headers):
    response = client.post("/api/v1/groups", json={"name": "IT Attempt"}, headers=it_headers)
    assert response.status_code == 403


def test_it_can_list_groups(client, it_headers, admin_headers):
    client.post("/api/v1/groups", json={"name": "Listable Group"}, headers=admin_headers)
    response = client.get("/api/v1/groups", headers=it_headers)
    assert response.status_code == 200
    assert any(g["name"] == "Listable Group" for g in response.json())


def test_employee_can_be_assigned_a_group(client, admin_headers):
    group = client.post("/api/v1/groups", json={"name": "Assign Target Group"}, headers=admin_headers).json()
    employee = client.post(
        "/api/v1/employees",
        json={"first_name": "Grouped", "last_name": "Employee", "email": "grouped.emp@ams-platform-tests.com"},
        headers=admin_headers,
    ).json()

    update = client.patch(
        f"/api/v1/employees/{employee['id']}", json={"group_id": group["id"]}, headers=admin_headers
    )
    assert update.status_code == 200
    assert update.json()["group_id"] == group["id"]