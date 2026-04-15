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
        chapter.content = (
            "<h1>Chapter 1</h1><p>Alpha topic content for retrieval.</p>"
            "<p>Beta details.</p>"
        )

        book.add_item(chapter)
        book.toc = (epub.Link("chap_1.xhtml", "Chapter 1", "chap1"),)
        book.spine = ["nav", chapter]
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        epub.write_epub(str(out), book)
        return out.read_bytes()


def test_query_preview_and_answer_with_citations():
    app = create_app()

    with TestClient(app) as client:
        ingest = client.post(
            "/api/v1/ingest/upload",
            files={"file": ("book.epub", _build_epub_bytes(), "application/epub+zip")},
        )
        assert ingest.status_code == 200
        book_id = ingest.json()["book_id"]

        preview = client.post(
            "/api/v1/query/preview",
            json={"question": "What is discussed?", "book_ids": [book_id], "top_k": 3},
        )
        assert preview.status_code == 200
        body = preview.json()
        assert body["diagnostics"]["retrieved_count"] >= 1
        assert len(body["evidence"]) >= 1

        answer = client.post(
            "/api/v1/query",
            json={"question": "What is discussed?", "book_ids": [book_id], "top_k": 3},
        )
        assert answer.status_code == 200
        payload = answer.json()
        assert isinstance(payload["answer"], str)
        assert len(payload["citations"]) >= 1
        assert payload["citations"][0]["chunk_id"]


def test_query_requires_retrieved_evidence():
    app = create_app()

    with TestClient(app) as client:
        answer = client.post(
            "/api/v1/query",
            json={"question": "anything", "book_ids": ["non-existent-book"], "top_k": 3},
        )
        assert answer.status_code == 400
        assert "No retrieved evidence" in answer.json()["detail"]
