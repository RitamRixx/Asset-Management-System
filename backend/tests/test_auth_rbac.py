"""Auth + RBAC tests (section 50: 'An employee cannot assign an asset', etc.)."""


def test_login_success(client, admin):
    _, token = admin
    assert token


def test_login_wrong_password_returns_401(client, admin):
    user, _ = admin
    response = client.post(
        "/api/v1/auth/login", json={"email": user.email, "password": "wrong-password"}
    )
    assert response.status_code == 401


def test_login_unknown_email_returns_401(client):
    response = client.post(
        "/api/v1/auth/login", json={"email": "nobody@ams-platform-tests.com", "password": "whatever"}
    )
    assert response.status_code == 401


def test_disabled_account_cannot_login(client, admin_headers, it_user):
    user, _ = it_user
    response = client.patch(
        f"/api/v1/users/{user.id}/status", json={"status": "DISABLED"}, headers=admin_headers
    )
    assert response.status_code == 200

    login = client.post("/api/v1/auth/login", json={"email": user.email, "password": "ItPass123!"})
    assert login.status_code == 401


def test_unauthenticated_request_returns_401(client):
    response = client.get("/api/v1/employees")
    assert response.status_code == 401


def test_employee_cannot_create_employee(client, employee_with_login):
    _, headers = employee_with_login
    response = client.post(
        "/api/v1/employees",
        json={"first_name": "New", "last_name": "Hire", "email": "new.hire@ams-platform-tests.com"},
        headers=headers,
    )
    assert response.status_code == 403


def test_employee_cannot_create_asset(client, employee_with_login, sample_asset_type):
    _, headers = employee_with_login
    response = client.post(
        "/api/v1/assets", json={"asset_type_id": sample_asset_type["id"]}, headers=headers
    )
    assert response.status_code == 403


def test_it_can_create_asset(client, it_headers, sample_asset_type):
    response = client.post(
        "/api/v1/assets", json={"asset_type_id": sample_asset_type["id"]}, headers=it_headers
    )
    assert response.status_code == 201


def test_employee_cannot_see_another_employees_record(client, employee_with_login, admin_headers):
    """Rule #14: 'Employees can only see their own assets' — extends to
    their profile record too, via require_self_or_role."""
    other = client.post(
        "/api/v1/employees",
        json={"first_name": "Other", "last_name": "Person", "email": "other.person@ams-platform-tests.com"},
        headers=admin_headers,
    ).json()

    _, headers = employee_with_login
    response = client.get(f"/api/v1/employees/{other['id']}", headers=headers)
    assert response.status_code == 403


def test_employee_can_see_own_record(client, employee_with_login):
    employee, headers = employee_with_login
    response = client.get(f"/api/v1/employees/{employee['id']}", headers=headers)
    assert response.status_code == 200


def test_employee_can_see_own_software_but_not_others(client, employee_with_login, admin_headers):
    """Regression test: /employees/{id}/software originally enforced
    STAFF_ROLES only, contradicting its own docstring and section 6
    ('View software assigned/installed to them'). Fixed to use
    require_self_or_role, same as the employee record endpoint itself."""
    employee, headers = employee_with_login

    own = client.get(f"/api/v1/employees/{employee['id']}/software", headers=headers)
    assert own.status_code == 200

    other_employee = client.post(
        "/api/v1/employees",
        json={"first_name": "Someone", "last_name": "Else", "email": "someone.else@ams-platform-tests.com"},
        headers=admin_headers,
    ).json()
    other = client.get(f"/api/v1/employees/{other_employee['id']}/software", headers=headers)
    assert other.status_code == 403
