from __future__ import annotations

from pathlib import Path

import httpx

from packages.ingest.adapters.epub_url import EpubUrlAdapter
from packages.ingest.adapters.miz_books import MizBooksAdapter
from packages.ingest.adapters.pdf_url import PdfUrlAdapter
from packages.ingest.adapters.uploaded_epub import UploadedEpubAdapter
from packages.ingest.adapters.uploaded_pdf import UploadedPdfAdapter


def test_uploaded_epub_snapshot(tmp_path: Path):
    adapter = UploadedEpubAdapter()
    payload = adapter.fetch(source_ref="demo.epub", upload_bytes=b"EPUB")

    out = adapter.snapshot(book_id="book-1", payload=payload, raw_root=tmp_path)

    assert out.exists()
    assert out.read_bytes() == b"EPUB"


def test_epub_url_adapter_can_handle():
    adapter = EpubUrlAdapter()
    assert adapter.can_handle(source_type="epub_url", source_ref="https://example.com/a.epub")


def test_miz_books_pattern_matching():
    adapter = MizBooksAdapter()
    assert adapter.can_handle(
        source_type="miz_books",
        source_ref="https://books.miz.com.tw/read/abc",
    )
    assert not adapter.can_handle(
        source_type="miz_books",
        source_ref="https://example.com/read/abc",
    )


def test_uploaded_pdf_snapshot(tmp_path: Path):
    adapter = UploadedPdfAdapter()
    payload = adapter.fetch(source_ref="demo.pdf", upload_bytes=b"%PDF-1.4")

    out = adapter.snapshot(book_id="book-2", payload=payload, raw_root=tmp_path)

    assert out.exists()
    assert out.read_bytes() == b"%PDF-1.4"


def test_uploaded_pdf_adapter_can_handle():
    adapter = UploadedPdfAdapter()
    assert adapter.can_handle(source_type="uploaded_pdf", source_ref="demo.pdf")


def test_uploaded_pdf_rejects_non_pdf_signature():
    adapter = UploadedPdfAdapter()
    try:
        adapter.fetch(source_ref="demo.pdf", upload_bytes=b"not-a-pdf")
    except ValueError as exc:
        assert "valid PDF file signature" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid PDF signature")


def test_pdf_url_adapter_can_handle():
    adapter = PdfUrlAdapter()
    assert adapter.can_handle(source_type="pdf_url", source_ref="https://example.com/a.pdf")


def test_pdf_url_adapter_fetch_and_snapshot(monkeypatch, tmp_path: Path):
    response = httpx.Response(
        status_code=200,
        headers={"content-type": "application/pdf", "content-length": "8"},
        content=b"%PDF-1.4",
        request=httpx.Request("GET", "https://example.com/book.pdf"),
    )

    captured: dict[str, object] = {}

    def _fake_get(*_args, **kwargs):
        captured.update(kwargs)
        return response

    monkeypatch.setattr("packages.ingest.adapters.pdf_url.httpx.get", _fake_get)
    monkeypatch.setattr(
        "packages.ingest.adapters.pdf_url.validate_public_http_url",
        lambda _url, **_kwargs: None,
    )

    adapter = PdfUrlAdapter()
    payload = adapter.fetch(source_ref="https://example.com/book.pdf")
    out = adapter.snapshot(book_id="book-3", payload=payload, raw_root=tmp_path)

    assert payload.metadata.source_type == "pdf_url"
    assert payload.metadata.original_filename == "book.pdf"
    assert payload.metadata.content_type == "application/pdf"
    assert out.exists()
    assert out.read_bytes() == b"%PDF-1.4"
    assert captured.get("trust_env") is False


def test_pdf_url_adapter_rejects_non_pdf_signature(monkeypatch):
    response = httpx.Response(
        status_code=200,
        headers={"content-type": "text/html"},
        content=b"<html>not a pdf</html>",
        request=httpx.Request("GET", "https://example.com/book.pdf"),
    )
    monkeypatch.setattr("packages.ingest.adapters.pdf_url.httpx.get", lambda *_, **__: response)
    monkeypatch.setattr(
        "packages.ingest.adapters.pdf_url.validate_public_http_url",
        lambda _url, **_kwargs: None,
    )

    adapter = PdfUrlAdapter()
    try:
        adapter.fetch(source_ref="https://example.com/book.pdf")
    except ValueError as exc:
        assert "valid PDF file signature" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid remote PDF signature")


def test_pdf_url_adapter_passes_allowlist_settings_to_validator(monkeypatch):
    response = httpx.Response(
        status_code=200,
        headers={"content-type": "application/pdf"},
        content=b"%PDF-1.4",
        request=httpx.Request("GET", "https://files.example.com/book.pdf"),
    )
    captured: dict[str, object] = {}

    def _fake_validate(source_ref: str, **kwargs):
        captured["source_ref"] = source_ref
        captured["allowlist_enabled"] = kwargs.get("allowlist_enabled")
        captured["allowlist_hosts"] = kwargs.get("allowlist_hosts")

    monkeypatch.setattr(
        "packages.ingest.adapters.pdf_url.validate_public_http_url",
        _fake_validate,
    )
    monkeypatch.setattr("packages.ingest.adapters.pdf_url.httpx.get", lambda *_, **__: response)

    adapter = PdfUrlAdapter(
        allowlist_enabled=True,
        allowlist_hosts=["example.com"],
    )
    adapter.fetch(source_ref="https://files.example.com/book.pdf")

    assert captured["source_ref"] == "https://files.example.com/book.pdf"
    assert captured["allowlist_enabled"] is True
    assert captured["allowlist_hosts"] == ["example.com"]
