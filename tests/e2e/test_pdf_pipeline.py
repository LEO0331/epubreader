from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.main import create_app

PDF_BYTES = b"%PDF-1.4\n"


def test_end_to_end_pdf_pipeline_text(monkeypatch):
    monkeypatch.setattr(
        "packages.parsing.parsing_service.parse_pdf",
        lambda *args, **kwargs: {
            "metadata": {
                "title": "PDF Demo",
                "author": None,
                "language": None,
                "toc": [],
                "ocr": {
                    "enabled": True,
                    "langs": "chi_tra+eng",
                    "min_text_chars": 80,
                    "attempted_pages": 0,
                    "used_pages": 0,
                    "available": True,
                },
            },
            "sections": [
                {
                    "ordinal": 0,
                    "heading": "Page 1",
                    "heading_path": ["Page 1"],
                    "content": "PDF pipeline text content.",
                    "source_locator": "page:1",
                }
            ],
        },
    )

    app = create_app()
    with TestClient(app) as client:
        ingest = client.post(
            "/api/v1/ingest/upload",
            files={"file": ("book.pdf", PDF_BYTES, "application/pdf")},
        )
        assert ingest.status_code == 200
        book_id = ingest.json()["book_id"]

        sections = client.get(f"/api/v1/books/{book_id}/sections")
        assert sections.status_code == 200
        assert sections.json()["count"] >= 1

        chunks = client.get(f"/api/v1/books/{book_id}/chunks")
        assert chunks.status_code == 200
        assert chunks.json()["count"] >= 1


def test_end_to_end_pdf_pipeline_scanned_metadata(monkeypatch):
    monkeypatch.setattr(
        "packages.parsing.parsing_service.parse_pdf",
        lambda *args, **kwargs: {
            "metadata": {
                "title": "Scanned Demo",
                "author": None,
                "language": None,
                "toc": [],
                "ocr": {
                    "enabled": True,
                    "langs": "chi_tra+eng",
                    "min_text_chars": 80,
                    "attempted_pages": 2,
                    "used_pages": 1,
                    "available": False,
                },
            },
            "sections": [
                {
                    "ordinal": 0,
                    "heading": "Page 2",
                    "heading_path": ["Page 2"],
                    "content": "OCR recovered content.",
                    "source_locator": "page:2",
                }
            ],
        },
    )

    app = create_app()
    with TestClient(app) as client:
        ingest = client.post(
            "/api/v1/ingest/upload",
            files={"file": ("scan.pdf", PDF_BYTES, "application/pdf")},
        )
        assert ingest.status_code == 200
        book_id = ingest.json()["book_id"]

        book = client.get(f"/api/v1/books/{book_id}")
        assert book.status_code == 200

        sections = client.get(f"/api/v1/books/{book_id}/sections")
        assert sections.status_code == 200
        payload = sections.json()
        assert payload["sections"][0]["source_locator"] == "page:2"
