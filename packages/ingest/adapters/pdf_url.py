from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from packages.ingest.adapters.base import RawSourcePayload, SourceAdapter, SourceMetadata
from packages.ingest.adapters.http_fetch import fetch_limited_bytes
from packages.ingest.adapters.url_security import validate_public_http_url

PDF_MAGIC = b"%PDF-"


class PdfUrlAdapter(SourceAdapter):
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
        return source_type == "pdf_url" and source_ref.startswith(("http://", "https://"))

    def fetch(self, *, source_ref: str, upload_bytes: bytes | None = None) -> RawSourcePayload:
        if upload_bytes is not None:
            raise ValueError("upload_bytes is not supported for pdf_url adapter")
        validate_public_http_url(
            source_ref,
            allowlist_enabled=self.allowlist_enabled,
            allowlist_hosts=self.allowlist_hosts,
        )

        fetched = fetch_limited_bytes(
            source_ref,
            max_bytes=self.max_bytes,
            resource_label="PDF",
        )
        if not fetched.content.startswith(PDF_MAGIC):
            raise ValueError("Remote payload is not a valid PDF file signature")

        filename = Path(urlparse(source_ref).path).name or "source.pdf"
        if not filename.lower().endswith(".pdf"):
            filename = f"{filename}.pdf"

        return RawSourcePayload(
            metadata=SourceMetadata(
                source_type="pdf_url",
                source_ref=source_ref,
                original_filename=filename,
                content_type=fetched.headers.get("content-type") or "application/pdf",
            ),
            content_bytes=fetched.content,
        )

    def extract_metadata(self, payload: RawSourcePayload) -> dict[str, str]:
        metadata = {"source_ref": payload.metadata.source_ref}
        if payload.metadata.original_filename:
            metadata["original_filename"] = payload.metadata.original_filename
        if payload.metadata.content_type:
            metadata["content_type"] = payload.metadata.content_type
        return metadata

    def snapshot(self, *, book_id: str, payload: RawSourcePayload, raw_root: Path) -> Path:
        out_dir = raw_root / book_id
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / (payload.metadata.original_filename or "source.pdf")
        out_path.write_bytes(payload.content_bytes)
        return out_path
