from __future__ import annotations

from fastapi import APIRouter
from fastapi.testclient import TestClient

from apps.api.main import create_app


def test_unhandled_exception_returns_stable_payload():
    app = create_app()

    router = APIRouter(prefix="/api/v1")

    @router.get("/boom")
    def boom() -> dict[str, str]:
        raise RuntimeError("boom")

    app.include_router(router)

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/api/v1/boom")

    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "internal_error"
    assert isinstance(body["error"]["request_id"], str)
