from __future__ import annotations

import tempfile
from pathlib import Path

from ebooklib import epub
from fastapi.testclient import TestClient

from apps.api.main import create_app


def _build_epub_bytes() -> bytes:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        out = tmp_path / "book.epub"

        book = epub.EpubBook()
        book.set_identifier("id-1")
        book.set_title("Demo")
        book.set_language("en")
        book.add_author("Author")

        chapter = epub.EpubHtml(title="Chapter 1", file_name="chap_1.xhtml", lang="en")
        chapter.content = "<h1>Chapter 1</h1><p>Hello world content.</p>"

        book.add_item(chapter)
        book.toc = (epub.Link("chap_1.xhtml", "Chapter 1", "chap1"),)
        book.spine = ["nav", chapter]
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        epub.write_epub(str(out), book)
        return out.read_bytes()


def test_upload_ingest_and_job_lookup():
    app = create_app()
    with TestClient(app) as client:
        upload = {"file": ("book.epub", _build_epub_bytes(), "application/epub+zip")}
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


def test_upload_ingest_rejects_non_epub_extension():
    app = create_app()
    with TestClient(app) as client:
        upload = {"file": ("book.txt", b"not-epub", "text/plain")}
        response = client.post("/api/v1/ingest/upload", files=upload)
        assert response.status_code == 400
        assert ".epub" in str(response.json()["detail"])


def test_upload_ingest_rejects_oversized_file(monkeypatch):
    monkeypatch.setenv("APP_INGEST_MAX_BYTES", "10")
    app = create_app()
    with TestClient(app) as client:
        upload = {"file": ("book.epub", b"01234567890", "application/epub+zip")}
        response = client.post("/api/v1/ingest/upload", files=upload)
        assert response.status_code == 413
