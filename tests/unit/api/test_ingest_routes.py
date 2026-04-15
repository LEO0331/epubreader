from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.main import create_app


def test_upload_ingest_and_job_lookup():
    app = create_app()
    with TestClient(app) as client:
        upload = {"file": ("book.epub", b"dummy-epub-content", "application/epub+zip")}
        response = client.post("/api/v1/ingest/upload", files=upload)

        assert response.status_code == 200
        payload = response.json()
        assert "book_id" in payload
        assert "job_id" in payload

        job_resp = client.get(f"/api/v1/jobs/{payload['job_id']}")
        assert job_resp.status_code == 200
        assert job_resp.json()["status"] == "completed"


def test_ingest_text_placeholder():
    app = create_app()
    with TestClient(app) as client:
        response = client.post("/api/v1/ingest/text", json={"text": "hello"})

        assert response.status_code == 200
        assert response.json()["status"] == "not_implemented"
