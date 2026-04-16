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
        assert ".epub or .pdf" in str(response.json()["detail"])


def test_upload_ingest_rejects_oversized_file(monkeypatch):
    monkeypatch.setenv("APP_INGEST_MAX_BYTES", "10")
    app = create_app()
    with TestClient(app) as client:
        upload = {"file": ("book.epub", b"01234567890", "application/epub+zip")}
        response = client.post("/api/v1/ingest/upload", files=upload)
        assert response.status_code == 413


def test_upload_pdf_ingest_and_job_lookup(monkeypatch):
    monkeypatch.setattr(
        "packages.parsing.parsing_service.parse_pdf",
        lambda *args, **kwargs: {
            "metadata": {"title": None, "author": None, "language": None, "toc": []},
            "sections": [
                {
                    "ordinal": 0,
                    "heading": "Page 1",
                    "heading_path": ["Page 1"],
                    "content": "PDF text",
                    "source_locator": "page:1",
                }
            ],
        },
    )

    app = create_app()
    with TestClient(app) as client:
        upload = {"file": ("book.pdf", b"%PDF-1.4\\n", "application/pdf")}
        response = client.post("/api/v1/ingest/upload", files=upload)

        assert response.status_code == 200
        payload = response.json()
        assert "book_id" in payload
        assert "job_id" in payload

        job_resp = client.get(f"/api/v1/jobs/{payload['job_id']}")
        assert job_resp.status_code == 200
        assert job_resp.json()["status"] == "completed"


def test_ingest_url_infers_pdf_source_type(monkeypatch):
    captured: dict[str, str] = {}

    def _fake_ingest_url(self, *, source_type: str, url: str):  # noqa: ANN001
        captured["source_type"] = source_type
        captured["url"] = url
        return {"book_id": "book-123", "job_id": "job-123"}

    monkeypatch.setattr("apps.api.routes.ingest.IngestionService.ingest_url", _fake_ingest_url)

    app = create_app()
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/ingest/url",
            json={"url": "https://example.com/sample.pdf"},
        )
        assert response.status_code == 200
        assert captured["source_type"] == "pdf_url"
        assert captured["url"] == "https://example.com/sample.pdf"


def test_ingest_url_infers_pdf_source_type_with_query(monkeypatch):
    captured: dict[str, str] = {}

    def _fake_ingest_url(self, *, source_type: str, url: str):  # noqa: ANN001
        captured["source_type"] = source_type
        captured["url"] = url
        return {"book_id": "book-123", "job_id": "job-123"}

    monkeypatch.setattr("apps.api.routes.ingest.IngestionService.ingest_url", _fake_ingest_url)

    app = create_app()
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/ingest/url",
            json={"url": "https://example.com/sample.pdf?download=1"},
        )
        assert response.status_code == 200
        assert captured["source_type"] == "pdf_url"
        assert captured["url"] == "https://example.com/sample.pdf?download=1"


def test_ingest_url_infers_epub_source_type_with_query(monkeypatch):
    captured: dict[str, str] = {}

    def _fake_ingest_url(self, *, source_type: str, url: str):  # noqa: ANN001
        captured["source_type"] = source_type
        captured["url"] = url
        return {"book_id": "book-123", "job_id": "job-123"}

    monkeypatch.setattr("apps.api.routes.ingest.IngestionService.ingest_url", _fake_ingest_url)

    app = create_app()
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/ingest/url",
            json={"url": "https://example.com/sample.epub?signature=abc"},
        )
        assert response.status_code == 200
        assert captured["source_type"] == "epub_url"
        assert captured["url"] == "https://example.com/sample.epub?signature=abc"
