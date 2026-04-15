from __future__ import annotations

from sqlalchemy.orm import Session

from packages.storage.db.models import BookORM


class BooksRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        *,
        book_id: str,
        source_type: str,
        source_ref: str,
        status: str,
        title: str | None = None,
        author: str | None = None,
        language: str | None = None,
    ) -> BookORM:
        book = BookORM(
            id=book_id,
            title=title,
            author=author,
            language=language,
            source_type=source_type,
            source_ref=source_ref,
            status=status,
        )
        self.session.add(book)
        self.session.flush()
        return book

    def get(self, book_id: str) -> BookORM | None:
        return self.session.get(BookORM, book_id)

    def list(self, *, limit: int = 100, offset: int = 0) -> list[BookORM]:
        return self.session.query(BookORM).offset(offset).limit(limit).all()

    def update_snapshot_path(self, book_id: str, snapshot_path: str) -> BookORM | None:
        book = self.get(book_id)
        if book is None:
            return None
        book.raw_snapshot_path = snapshot_path
        self.session.flush()
        return book
