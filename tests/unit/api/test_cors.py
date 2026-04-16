from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.main import create_app


def test_cors_allows_configured_origin(monkeypatch):
    monkeypatch.setenv("APP_CORS_ALLOW_ORIGINS", "https://example.com")

    app = create_app()
    client = TestClient(app)

    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "https://example.com"
