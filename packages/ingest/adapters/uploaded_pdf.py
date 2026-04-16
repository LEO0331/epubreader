from __future__ import annotations

from pathlib import Path

from packages.ingest.adapters.base import RawSourcePayload, SourceAdapter, SourceMetadata

PDF_MAGIC = b"%PDF-"


class UploadedPdfAdapter(SourceAdapter):
    def can_handle(self, *, source_type: str, source_ref: str) -> bool:
        return source_type == "uploaded_pdf"

    def fetch(self, *, source_ref: str, upload_bytes: bytes | None = None) -> RawSourcePayload:
        if upload_bytes is None:
            raise ValueError("upload_bytes is required for uploaded_pdf adapter")
        if not upload_bytes.startswith(PDF_MAGIC):
            raise ValueError("Uploaded payload is not a valid PDF file signature")

        filename = Path(source_ref).name or "upload.pdf"
        if not filename.lower().endswith(".pdf"):
            filename = f"{filename}.pdf"

        return RawSourcePayload(
            metadata=SourceMetadata(
                source_type="uploaded_pdf",
                source_ref=source_ref,
                original_filename=filename,
                content_type="application/pdf",
            ),
            content_bytes=upload_bytes,
        )

    def extract_metadata(self, payload: RawSourcePayload) -> dict[str, str]:
        result = {"source_ref": payload.metadata.source_ref}
        if payload.metadata.original_filename:
            result["original_filename"] = payload.metadata.original_filename
        if payload.metadata.content_type:
            result["content_type"] = payload.metadata.content_type
        return result

    def snapshot(self, *, book_id: str, payload: RawSourcePayload, raw_root: Path) -> Path:
        out_dir = raw_root / book_id
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / (payload.metadata.original_filename or "upload.pdf")
        out_path.write_bytes(payload.content_bytes)
        return out_path
