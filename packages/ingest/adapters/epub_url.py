from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import httpx

from packages.ingest.adapters.base import RawSourcePayload, SourceAdapter, SourceMetadata


class EpubUrlAdapter(SourceAdapter):
    def can_handle(self, *, source_type: str, source_ref: str) -> bool:
        return source_type == "epub_url" and source_ref.startswith(("http://", "https://"))

    def fetch(self, *, source_ref: str, upload_bytes: bytes | None = None) -> RawSourcePayload:
        if upload_bytes is not None:
            raise ValueError("upload_bytes is not supported for epub_url adapter")

        response = httpx.get(source_ref, timeout=30)
        response.raise_for_status()

        filename = Path(urlparse(source_ref).path).name or "source.epub"
        return RawSourcePayload(
            metadata=SourceMetadata(
                source_type="epub_url",
                source_ref=source_ref,
                original_filename=filename,
                content_type=response.headers.get("content-type"),
            ),
            content_bytes=response.content,
        )

    def extract_metadata(self, payload: RawSourcePayload) -> dict[str, str]:
        metadata = {
            "source_ref": payload.metadata.source_ref,
        }
        if payload.metadata.original_filename:
            metadata["original_filename"] = payload.metadata.original_filename
        return metadata

    def snapshot(self, *, book_id: str, payload: RawSourcePayload, raw_root: Path) -> Path:
        out_dir = raw_root / book_id
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / (payload.metadata.original_filename or "source.epub")
        out_path.write_bytes(payload.content_bytes)
        return out_path
