from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.main import create_app


def test_health_endpoint_returns_ok():
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "X-Request-ID" in response.headers
