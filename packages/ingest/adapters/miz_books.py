from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import httpx

from packages.ingest.adapters.base import RawSourcePayload, SourceAdapter, SourceMetadata


class MizBooksAdapter(SourceAdapter):
    def can_handle(self, *, source_type: str, source_ref: str) -> bool:
        if source_type != "miz_books":
            return False
        parsed = urlparse(source_ref)
        return (
            parsed.scheme in {"http", "https"}
            and parsed.netloc == "books.miz.com.tw"
            and parsed.path.startswith("/read/")
        )

    def fetch(self, *, source_ref: str, upload_bytes: bytes | None = None) -> RawSourcePayload:
        if upload_bytes is not None:
            raise ValueError("upload_bytes is not supported for miz_books adapter")

        response = httpx.get(source_ref, timeout=30)
        response.raise_for_status()

        return RawSourcePayload(
            metadata=SourceMetadata(
                source_type="miz_books",
                source_ref=source_ref,
                original_filename="source.html",
                content_type=response.headers.get("content-type") or "text/html",
            ),
            content_bytes=response.content,
        )

    def extract_metadata(self, payload: RawSourcePayload) -> dict[str, str]:
        return {
            "source_ref": payload.metadata.source_ref,
            "content_type": payload.metadata.content_type or "text/html",
        }

    def snapshot(self, *, book_id: str, payload: RawSourcePayload, raw_root: Path) -> Path:
        out_dir = raw_root / book_id
        out_dir.mkdir(parents=True, exist_ok=True)
        suffix = ".html"
        out_path = out_dir / f"source{suffix}"
        out_path.write_bytes(payload.content_bytes)
        return out_path
