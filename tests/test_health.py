"""Test health endpoints."""
from fastapi.testclient import TestClient

from src.main import app


def test_health_check():
    """Test basic health check."""
    client = TestClient(app)
    response = client.get("/health/")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "PersonaKit"
    assert data["version"] == "0.1.0"
    assert "timestamp" in data
