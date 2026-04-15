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
        chapter.content = "<h1>Chapter 1</h1><p>Alpha pipeline content.</p><p>Beta content.</p>"

        book.add_item(chapter)
        book.toc = (epub.Link("chap_1.xhtml", "Chapter 1", "chap1"),)
        book.spine = ["nav", chapter]
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        epub.write_epub(str(out), book)
        return out.read_bytes()


def test_end_to_end_pipeline():
    app = create_app()

    with TestClient(app) as client:
        ingest = client.post(
            "/api/v1/ingest/upload",
            files={"file": ("book.epub", _build_epub_bytes(), "application/epub+zip")},
        )
        assert ingest.status_code == 200
        ids = ingest.json()
        book_id = ids["book_id"]
        job_id = ids["job_id"]

        job = client.get(f"/api/v1/jobs/{job_id}")
        assert job.status_code == 200

        sections = client.get(f"/api/v1/books/{book_id}/sections")
        assert sections.status_code == 200
        assert sections.json()["count"] >= 1

        chunks = client.get(f"/api/v1/books/{book_id}/chunks")
        assert chunks.status_code == 200
        assert chunks.json()["count"] >= 1

        artifacts = client.post(
            f"/api/v1/books/{book_id}/artifacts/build",
            json={"include_skill": True},
        )
        assert artifacts.status_code == 200

        query = client.post(
            "/api/v1/query",
            json={"question": "What is discussed?", "book_ids": [book_id], "top_k": 3},
        )
        assert query.status_code == 200
        result = query.json()
        assert isinstance(result["answer"], str)
        assert len(result["citations"]) >= 1
