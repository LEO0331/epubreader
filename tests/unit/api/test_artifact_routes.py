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


def test_artifact_build_and_fetch_routes():
    app = create_app()

    with TestClient(app) as client:
        ingest = client.post(
            "/api/v1/ingest/upload",
            files={"file": ("book.epub", _build_epub_bytes(), "application/epub+zip")},
        )
        assert ingest.status_code == 200
        book_id = ingest.json()["book_id"]

        build = client.post(
            f"/api/v1/books/{book_id}/artifacts/build",
            json={"include_skill": True},
        )
        assert build.status_code == 200
        assert build.json()["book_id"] == book_id

        listing = client.get(f"/api/v1/books/{book_id}/artifacts")
        assert listing.status_code == 200
        assert len(listing.json()) >= 3

        summary = client.get(f"/api/v1/books/{book_id}/artifacts/summary")
        assert summary.status_code == 200
        assert isinstance(summary.json()["content"], str)
