"""
Smoke test for Phase 1: confirms the FastAPI app boots and the health
endpoint responds. Real business-rule tests (section 50 of the spec) start
arriving alongside their features from Phase 6 onward.

Requires DATABASE_URL to point at a reachable Postgres instance (see
docker-compose.yml). Run with: pytest
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
