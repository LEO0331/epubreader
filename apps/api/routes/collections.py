from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from packages.core.config.loader import get_settings
from packages.exporters import export_filesystem, export_github, export_obsidian
from packages.services.collection_service import (
    CollectionBookNotFoundError,
    CollectionNotFoundError,
    CollectionService,
)
from packages.storage.db.session import get_db_session
from packages.storage.repositories.artifacts_repo import ArtifactsRepository
from packages.storage.repositories.books_repo import BooksRepository

router = APIRouter(prefix="/collections", tags=["collections"])


class CollectionCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class CollectionBookRequest(BaseModel):
    book_id: str = Field(min_length=1)


class ExportRequest(BaseModel):
    target: str = Field(pattern="^(filesystem|obsidian|github)$")
    output_dir: str | None = None
    obsidian_profile: str = Field(default="basic", pattern="^(basic|enhanced)$")


def _resolve_export_output_dir(output_dir: str | None) -> Path:
    base = (Path(get_settings().storage.data_dir) / "exports").resolve()
    if output_dir is None:
        return base

    requested = Path(output_dir)
    if requested.is_absolute():
        raise HTTPException(status_code=400, detail="output_dir must be relative")

    resolved = (base / requested).resolve()
    if base != resolved and base not in resolved.parents:
        raise HTTPException(status_code=400, detail="output_dir must stay within data exports")

    return resolved


@router.post("")
def create_collection(
    payload: CollectionCreateRequest,
    db: Session = Depends(get_db_session),
) -> dict[str, object]:
    return CollectionService(db).create_collection(name=payload.name)


@router.get("")
def list_collections(db: Session = Depends(get_db_session)) -> list[dict[str, object]]:
    return CollectionService(db).list_collections()


@router.get("/{collection_id}")
def get_collection(collection_id: str, db: Session = Depends(get_db_session)) -> dict[str, object]:
    row = CollectionService(db).get_collection(collection_id=collection_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Collection not found: {collection_id}")
    return row


@router.post("/{collection_id}/books")
def add_book(
    collection_id: str,
    payload: CollectionBookRequest,
    db: Session = Depends(get_db_session),
) -> dict[str, str]:
    try:
        return CollectionService(db).add_book(collection_id=collection_id, book_id=payload.book_id)
    except (CollectionBookNotFoundError, CollectionNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{collection_id}/books/{book_id}")
def remove_book(
    collection_id: str,
    book_id: str,
    db: Session = Depends(get_db_session),
) -> dict[str, str]:
    try:
        return CollectionService(db).remove_book(collection_id=collection_id, book_id=book_id)
    except CollectionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{collection_id}/export")
def export_collection(
    collection_id: str,
    payload: ExportRequest,
    db: Session = Depends(get_db_session),
) -> dict[str, object]:
    service = CollectionService(db)
    collection = service.get_collection(collection_id=collection_id)
    if collection is None:
        raise HTTPException(status_code=404, detail=f"Collection not found: {collection_id}")

    books_repo = BooksRepository(db)
    artifacts_repo = ArtifactsRepository(db)
    data_dir = Path(get_settings().storage.data_dir).resolve()

    book_ids_raw = collection.get("book_ids")
    book_ids = [str(x) for x in book_ids_raw] if isinstance(book_ids_raw, list) else []

    books_data: list[dict[str, object]] = []
    for book_id in book_ids:
        book = books_repo.get(book_id)
        if book is None:
            continue
        summary = artifacts_repo.get_latest_by_type(book_id=book.id, artifact_type="summary")
        wiki = artifacts_repo.get_latest_by_type(book_id=book.id, artifact_type="wiki")
        qa = artifacts_repo.get_latest_by_type(book_id=book.id, artifact_type="qa")

        summary_path = _safe_artifact_path(summary.path if summary else "", data_dir=data_dir)
        wiki_path = _safe_artifact_path(wiki.path if wiki else "", data_dir=data_dir)
        qa_path = _safe_artifact_path(qa.path if qa else "", data_dir=data_dir)

        books_data.append(
            {
                "id": book.id,
                "title": book.title or "",
                "source_type": book.source_type,
                "summary": summary_path.read_text(encoding="utf-8") if summary_path else "",
                "wiki": wiki_path.read_text(encoding="utf-8") if wiki_path else "",
                "qa": qa_path.read_text(encoding="utf-8") if qa_path else "",
                "summary_path": str(summary_path) if summary_path else "",
                "wiki_path": str(wiki_path) if wiki_path else "",
            }
        )

    output_dir = _resolve_export_output_dir(payload.output_dir)

    target_path: Path
    if payload.target == "filesystem":
        target_path = export_filesystem(
            output_dir=output_dir,
            collection_name=str(collection["name"]),
            books=books_data,
        )
    elif payload.target == "obsidian":
        target_path = export_obsidian(
            output_dir=output_dir,
            collection_name=str(collection["name"]),
            books=books_data,
            profile=payload.obsidian_profile,
        )
    else:
        target_path = export_github(
            output_dir=output_dir,
            collection_name=str(collection["name"]),
            books=books_data,
        )

    return {
        "collection_id": collection_id,
        "target": payload.target,
        "path": str(target_path),
        "book_count": len(books_data),
    }


def _safe_artifact_path(path: str, *, data_dir: Path) -> Path | None:
    if not path:
        return None
    resolved = Path(path).resolve()
    if not _is_within_root(resolved, data_dir):
        return None
    if not resolved.exists() or not resolved.is_file():
        return None
    return resolved


def _is_within_root(candidate: Path, root: Path) -> bool:
    if candidate == root:
        return True
    return root in candidate.parents
