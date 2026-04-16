from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.main import create_app


def test_api_key_middleware_allows_health_without_key(monkeypatch):
    monkeypatch.setenv("APP_API_KEY", "secret-1")
    app = create_app()

    with TestClient(app) as client:
        health = client.get("/api/v1/health")
        assert health.status_code == 200


def test_api_key_middleware_blocks_missing_or_invalid_key(monkeypatch):
    monkeypatch.setenv("APP_API_KEY", "secret-1")
    app = create_app()

    with TestClient(app) as client:
        blocked = client.get("/api/v1/books")
        assert blocked.status_code == 401

        invalid = client.get("/api/v1/books", headers={"X-API-Key": "wrong"})
        assert invalid.status_code == 401


def test_api_key_middleware_allows_valid_key(monkeypatch):
    monkeypatch.setenv("APP_API_KEY", "secret-1")
    app = create_app()

    with TestClient(app) as client:
        allowed = client.get("/api/v1/books", headers={"X-API-Key": "secret-1"})
        assert allowed.status_code == 200
