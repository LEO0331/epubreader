from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from packages.ingest.adapters.base import RawSourcePayload, SourceAdapter, SourceMetadata
from packages.ingest.adapters.http_fetch import fetch_limited_bytes
from packages.ingest.adapters.url_security import validate_public_http_url


class MizBooksAdapter(SourceAdapter):
    def __init__(
        self,
        *,
        max_bytes: int = 50 * 1024 * 1024,
        allowlist_enabled: bool = False,
        allowlist_hosts: list[str] | None = None,
    ):
        self.max_bytes = max_bytes
        self.allowlist_enabled = allowlist_enabled
        self.allowlist_hosts = allowlist_hosts or []

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
        validate_public_http_url(
            source_ref,
            allowlist_enabled=self.allowlist_enabled,
            allowlist_hosts=self.allowlist_hosts,
        )

        fetched = fetch_limited_bytes(
            source_ref,
            max_bytes=self.max_bytes,
            resource_label="source",
        )

        return RawSourcePayload(
            metadata=SourceMetadata(
                source_type="miz_books",
                source_ref=source_ref,
                original_filename="source.html",
                content_type=fetched.headers.get("content-type") or "text/html",
            ),
            content_bytes=fetched.content,
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
