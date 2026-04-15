from __future__ import annotations

from sqlalchemy.orm import Session

from packages.storage.db.models import BookORM
from packages.storage.repositories.books_repo import BooksRepository
from packages.storage.repositories.sections_repo import SectionsRepository


class BookInspectionService:
    def __init__(self, session: Session):
        self.books = BooksRepository(session)
        self.sections = SectionsRepository(session)

    def list_books(self, *, limit: int = 100, offset: int = 0) -> list[dict[str, object]]:
        rows = self.books.list(limit=limit, offset=offset)
        return [self._serialize_book(row) for row in rows]

    def get_book(self, *, book_id: str) -> dict[str, object] | None:
        row = self.books.get(book_id)
        if row is None:
            return None
        return self._serialize_book(row)

    def list_sections(
        self,
        *,
        book_id: str,
        limit: int = 200,
        offset: int = 0,
    ) -> list[dict[str, object]]:
        rows = self.sections.list_by_book(book_id, limit=limit, offset=offset)
        return [
            {
                "id": row.id,
                "book_id": row.book_id,
                "ordinal": row.ordinal,
                "heading": row.heading,
                "heading_path": [x for x in row.heading_path.split(" > ") if x.strip()],
                "content": row.content,
                "source_locator": row.source_locator,
            }
            for row in rows
        ]

    def _serialize_book(self, row: BookORM) -> dict[str, object]:
        return {
            "id": row.id,
            "title": row.title,
            "author": row.author,
            "language": row.language,
            "status": row.status,
            "source_type": row.source_type,
            "source_ref": row.source_ref,
            "raw_snapshot_path": row.raw_snapshot_path,
            "parse_quality_score": row.parse_quality_score,
            "created_at": row.created_at.isoformat(),
            "updated_at": row.updated_at.isoformat(),
        }
