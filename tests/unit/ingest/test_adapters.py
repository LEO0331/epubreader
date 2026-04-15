from __future__ import annotations

from pathlib import Path

from packages.ingest.adapters.epub_url import EpubUrlAdapter
from packages.ingest.adapters.miz_books import MizBooksAdapter
from packages.ingest.adapters.uploaded_epub import UploadedEpubAdapter


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
