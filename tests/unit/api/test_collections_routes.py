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
        chapter.content = "<h1>Chapter 1</h1><p>Collection scope content.</p>"

        book.add_item(chapter)
        book.toc = (epub.Link("chap_1.xhtml", "Chapter 1", "chap1"),)
        book.spine = ["nav", chapter]
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        epub.write_epub(str(out), book)
        return out.read_bytes()


def test_collection_scope_query_and_export():
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

        created = client.post("/api/v1/collections", json={"name": "My Set"})
        assert created.status_code == 200
        collection_id = created.json()["id"]

        added = client.post(f"/api/v1/collections/{collection_id}/books", json={"book_id": book_id})
        assert added.status_code == 200

        query = client.post(
            "/api/v1/query",
            json={"question": "What is the topic?", "collection_id": collection_id, "top_k": 3},
        )
        assert query.status_code == 200
        assert len(query.json()["citations"]) >= 1

        export = client.post(
            f"/api/v1/collections/{collection_id}/export",
            json={"target": "obsidian"},
        )
        assert export.status_code == 200
        assert export.json()["book_count"] >= 1
        assert "obsidian" in export.json()["path"]


def test_collection_export_rejects_absolute_output_dir():
    app = create_app()

    with TestClient(app) as client:
        created = client.post("/api/v1/collections", json={"name": "My Set"})
        assert created.status_code == 200
        collection_id = created.json()["id"]

        export = client.post(
            f"/api/v1/collections/{collection_id}/export",
            json={"target": "filesystem", "output_dir": "/tmp/out"},
        )
        assert export.status_code == 400
        assert "output_dir" in str(export.json()["detail"])


def test_collection_export_accepts_enhanced_obsidian_profile():
    app = create_app()

    with TestClient(app) as client:
        created = client.post("/api/v1/collections", json={"name": "My Set"})
        assert created.status_code == 200
        collection_id = created.json()["id"]

        export = client.post(
            f"/api/v1/collections/{collection_id}/export",
            json={"target": "obsidian", "obsidian_profile": "enhanced"},
        )
        assert export.status_code == 200
        assert export.json()["target"] == "obsidian"


def test_collection_export_ignores_obsidian_profile_for_filesystem_target():
    app = create_app()

    with TestClient(app) as client:
        created = client.post("/api/v1/collections", json={"name": "My Set"})
        assert created.status_code == 200
        collection_id = created.json()["id"]

        export = client.post(
            f"/api/v1/collections/{collection_id}/export",
            json={"target": "filesystem", "obsidian_profile": "enhanced"},
        )
        assert export.status_code == 200
        assert export.json()["target"] == "filesystem"


def test_collection_add_book_rejects_missing_book():
    app = create_app()

    with TestClient(app) as client:
        created = client.post("/api/v1/collections", json={"name": "My Set"})
        assert created.status_code == 200
        collection_id = created.json()["id"]

        added = client.post(
            f"/api/v1/collections/{collection_id}/books",
            json={"book_id": "missing-book"},
        )

        assert added.status_code == 404
        assert "Book not found" in added.json()["detail"]


def test_collection_add_book_rejects_missing_collection():
    app = create_app()

    with TestClient(app) as client:
        added = client.post(
            "/api/v1/collections/missing-collection/books",
            json={"book_id": "missing-book"},
        )

        assert added.status_code == 404
        assert "Collection not found" in added.json()["detail"]
