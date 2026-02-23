"""
Tests for main application.
"""
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_info(client: TestClient):
    """Test API info endpoint."""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.0"
    assert data["status"] == "active"
