from __future__ import annotations

from pathlib import Path

from packages.ingest.adapters.base import RawSourcePayload, SourceAdapter, SourceMetadata


class UploadedEpubAdapter(SourceAdapter):
    def can_handle(self, *, source_type: str, source_ref: str) -> bool:
        return source_type == "uploaded_epub"

    def fetch(self, *, source_ref: str, upload_bytes: bytes | None = None) -> RawSourcePayload:
        if upload_bytes is None:
            raise ValueError("upload_bytes is required for uploaded_epub adapter")

        return RawSourcePayload(
            metadata=SourceMetadata(
                source_type="uploaded_epub",
                source_ref=source_ref,
                original_filename=Path(source_ref).name or "upload.epub",
                content_type="application/epub+zip",
            ),
            content_bytes=upload_bytes,
        )

    def extract_metadata(self, payload: RawSourcePayload) -> dict[str, str]:
        result = {"source_ref": payload.metadata.source_ref}
        if payload.metadata.original_filename:
            result["original_filename"] = payload.metadata.original_filename
        return result

    def snapshot(self, *, book_id: str, payload: RawSourcePayload, raw_root: Path) -> Path:
        out_dir = raw_root / book_id
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / (payload.metadata.original_filename or "upload.epub")
        out_path.write_bytes(payload.content_bytes)
        return out_path
