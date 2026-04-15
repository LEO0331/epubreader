from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from packages.services.book_inspection_service import BookInspectionService
from packages.storage.db.session import get_db_session

router = APIRouter(prefix="/books", tags=["books"])


@router.get("")
def list_books(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db_session),
) -> list[dict[str, object]]:
    service = BookInspectionService(db)
    return service.list_books(limit=limit, offset=offset)


@router.get("/{book_id}")
def get_book(book_id: str, db: Session = Depends(get_db_session)) -> dict[str, object]:
    service = BookInspectionService(db)
    book = service.get_book(book_id=book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book not found: {book_id}")
    return book


@router.get("/{book_id}/sections")
def get_sections(
    book_id: str,
    limit: int = Query(default=200, ge=1, le=2000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db_session),
) -> dict[str, object]:
    service = BookInspectionService(db)
    if service.get_book(book_id=book_id) is None:
        raise HTTPException(status_code=404, detail=f"Book not found: {book_id}")

    sections = service.list_sections(book_id=book_id, limit=limit, offset=offset)
    return {
        "book_id": book_id,
        "count": len(sections),
        "limit": limit,
        "offset": offset,
        "sections": sections,
    }


@router.get("/{book_id}/chunks")
def get_chunks(
    book_id: str,
    limit: int = Query(default=200, ge=1, le=2000),
    offset: int = Query(default=0, ge=0),
    section_id: str | None = Query(default=None),
    db: Session = Depends(get_db_session),
) -> dict[str, object]:
    service = BookInspectionService(db)
    if service.get_book(book_id=book_id) is None:
        raise HTTPException(status_code=404, detail=f"Book not found: {book_id}")

    chunks = service.list_chunks(
        book_id=book_id,
        limit=limit,
        offset=offset,
        section_id=section_id,
    )
    return {
        "book_id": book_id,
        "count": len(chunks),
        "limit": limit,
        "offset": offset,
        "section_id": section_id,
        "chunks": chunks,
    }
