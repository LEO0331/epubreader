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
        chapter.content = "<h1>Chapter 1</h1><p>Hello world content.</p><p>Second paragraph.</p>"

        book.add_item(chapter)
        book.toc = (epub.Link("chap_1.xhtml", "Chapter 1", "chap1"),)
        book.spine = ["nav", chapter]

        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        epub.write_epub(str(out), book)
        return out.read_bytes()


def test_books_and_sections_routes_after_ingest_upload():
    app = create_app()

    with TestClient(app) as client:
        upload = {
            "file": (
                "book.epub",
                _build_epub_bytes(),
                "application/epub+zip",
            )
        }
        ingest = client.post("/api/v1/ingest/upload", files=upload)
        assert ingest.status_code == 200

        book_id = ingest.json()["book_id"]

        list_resp = client.get("/api/v1/books")
        assert list_resp.status_code == 200
        assert any(row["id"] == book_id for row in list_resp.json())

        detail = client.get(f"/api/v1/books/{book_id}")
        assert detail.status_code == 200
        assert detail.json()["parse_quality_score"] is not None
        assert detail.json()["status"] == "chunked"

        sections = client.get(f"/api/v1/books/{book_id}/sections")
        assert sections.status_code == 200
        body = sections.json()
        assert body["book_id"] == book_id
        assert body["count"] >= 1
        assert isinstance(body["sections"][0]["heading_path"], list)

        chunks = client.get(f"/api/v1/books/{book_id}/chunks")
        assert chunks.status_code == 200
        chunks_body = chunks.json()
        assert chunks_body["book_id"] == book_id
        assert chunks_body["count"] >= 1
        assert "metadata" in chunks_body["chunks"][0]
