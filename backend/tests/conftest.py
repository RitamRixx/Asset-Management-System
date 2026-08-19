"""
Shared pytest fixtures.

Runs against the same Postgres instance the app itself uses (see
DATABASE_URL in .env) — there's no separate SQLite/in-memory substitute,
because several behaviors under test (the departments<->employees circular
FK, Postgres ENUM types, unique constraints) only exist on Postgres. The
`_fresh_schema` fixture wipes and recreates every table once per test
session, so running the suite resets local dev data — expected for a
local run; a CI pipeline would point this at a disposable database via
DATABASE_URL instead.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as SQLASession

from app.core.database import Base, engine, get_db
from app.core.permissions import Role
from app.core.security import hash_password
from app.main import app
from app.models.enums import UserStatus
from app.models.user import User

from app import models  # noqa: F401  -- registers every mapped class


@pytest.fixture(scope="session", autouse=True)
def _fresh_schema():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def db_session():
    """
    One test = one outer transaction that's always rolled back, with the
    ORM session set to open a SAVEPOINT per logical unit of work
    (`join_transaction_mode="create_savepoint"`). App code calling
    `db.commit()` (every service in this codebase does, at the API layer)
    just releases/reopens a savepoint instead of committing for real, so
    nothing survives past this fixture's teardown — tests never see each
    other's data, no matter what they insert.
    """
    connection = engine.connect()
    outer_transaction = connection.begin()
    session = SQLASession(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        outer_transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _make_user_and_login(client, db_session, *, email: str, password: str, role: Role, employee_id=None):
    user = User(
        email=email,
        password_hash=hash_password(password),
        role=role,
        status=UserStatus.ACTIVE,
        employee_id=employee_id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return user, response.json()["access_token"]


@pytest.fixture
def admin(client, db_session):
    return _make_user_and_login(
        client, db_session, email="admin@ams-platform-tests.com", password="AdminPass123!", role=Role.ADMIN
    )


@pytest.fixture
def admin_headers(admin):
    _, token = admin
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def it_user(client, db_session):
    return _make_user_and_login(
        client, db_session, email="it@ams-platform-tests.com", password="ItPass123!", role=Role.IT_SUPPORT
    )


@pytest.fixture
def it_headers(it_user):
    _, token = it_user
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def hr_user(client, db_session):
    return _make_user_and_login(
        client, db_session, email="hr@ams-platform-tests.com", password="HrPass123!", role=Role.HR
    )


@pytest.fixture
def hr_headers(hr_user):
    _, token = hr_user
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_employee(client, admin_headers):
    """A plain Employee row (no User/login attached) for FK targets."""
    response = client.post(
        "/api/v1/employees",
        json={"first_name": "Test", "last_name": "Employee", "email": "sample.emp@ams-platform-tests.com"},
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def employee_with_login(client, db_session, sample_employee):
    """An Employee row *with* a linked User, so it can log in and hit
    self-scoped endpoints (rule #14 tests need this)."""
    user, token = _make_user_and_login(
        client,
        db_session,
        email="employee.login@ams-platform-tests.com",
        password="EmployeePass123!",
        role=Role.EMPLOYEE,
        employee_id=sample_employee["id"],
    )
    return sample_employee, {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_asset_type(client, admin_headers):
    response = client.post("/api/v1/asset-types", json={"name": "Test Laptop Type"}, headers=admin_headers)
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def sample_asset(client, admin_headers, sample_asset_type):
    response = client.post(
        "/api/v1/assets",
        json={"asset_type_id": sample_asset_type["id"], "manufacturer": "TestCo", "model": "T100"},
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def sample_component_type(client, admin_headers):
    response = client.post("/api/v1/component-types", json={"name": "Test RAM"}, headers=admin_headers)
    assert response.status_code == 201, response.text
    return response.json()
