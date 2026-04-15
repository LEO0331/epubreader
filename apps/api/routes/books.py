from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from packages.storage.db.session import get_db_session
from packages.storage.repositories.books_repo import BooksRepository

router = APIRouter(prefix="/books", tags=["books"])


@router.get("")
def list_books(db: Session = Depends(get_db_session)) -> list[dict[str, object]]:
    repo = BooksRepository(db)
    rows = repo.list()
    return [
        {
            "id": row.id,
            "title": row.title,
            "status": row.status,
            "source_type": row.source_type,
            "source_ref": row.source_ref,
            "raw_snapshot_path": row.raw_snapshot_path,
        }
        for row in rows
    ]
