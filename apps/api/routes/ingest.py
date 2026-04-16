from __future__ import annotations

from urllib.parse import urlparse

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from packages.core.config.loader import get_settings
from packages.services.ingestion_service import IngestionService
from packages.storage.db.session import get_db_session

router = APIRouter(prefix="/ingest", tags=["ingest"])


class IngestUrlRequest(BaseModel):
    url: str
    source_type: str | None = None


class IngestResponse(BaseModel):
    book_id: str
    job_id: str


def _detect_source_type(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.lower()
    if parsed.netloc == "books.miz.com.tw" and parsed.path.startswith("/read/"):
        return "miz_books"
    if path.endswith(".pdf"):
        return "pdf_url"
    if path.endswith(".epub"):
        return "epub_url"
    raise ValueError("Unable to infer source_type for URL; provide source_type explicitly")


def _detect_upload_source_type(filename: str) -> str:
    lower = filename.lower()
    if lower.endswith(".epub"):
        return "uploaded_epub"
    if lower.endswith(".pdf"):
        return "uploaded_pdf"
    raise ValueError("Uploaded file must be an .epub or .pdf file")


@router.post("/url", response_model=IngestResponse)
def ingest_url(payload: IngestUrlRequest, db: Session = Depends(get_db_session)) -> IngestResponse:
    settings = get_settings()
    source_type = payload.source_type or _detect_source_type(payload.url)
    service = IngestionService(
        db,
        data_root=settings.storage.data_dir,
        max_ingest_bytes=settings.app.ingest_max_bytes,
        host_allowlist_enabled=settings.app.ingest_host_allowlist_enabled,
        host_allowlist=settings.app.ingest_host_allowlist,
    )
    try:
        result = service.ingest_url(source_type=source_type, url=payload.url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return IngestResponse(**result)


@router.post("/upload", response_model=IngestResponse)
async def ingest_upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db_session),
) -> IngestResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename")
    try:
        source_type = _detect_upload_source_type(file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    settings = get_settings()
    payload = await file.read(settings.app.ingest_max_bytes + 1)
    if len(payload) > settings.app.ingest_max_bytes:
        raise HTTPException(status_code=413, detail="Uploaded file exceeds maximum allowed size")

    service = IngestionService(
        db,
        data_root=settings.storage.data_dir,
        max_ingest_bytes=settings.app.ingest_max_bytes,
        host_allowlist_enabled=settings.app.ingest_host_allowlist_enabled,
        host_allowlist=settings.app.ingest_host_allowlist,
    )
    result = service.ingest_upload(
        source_type=source_type,
        filename=file.filename,
        upload_bytes=payload,
    )
    return IngestResponse(**result)


class IngestTextPlaceholderRequest(BaseModel):
    text: str


@router.post("/text")
def ingest_text(_: IngestTextPlaceholderRequest) -> dict[str, str]:
    return {
        "status": "not_implemented",
        "message": "Text ingestion will be implemented in a later task.",
    }
