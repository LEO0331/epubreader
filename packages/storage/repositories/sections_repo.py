from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from packages.storage.db.models import SectionORM


class SectionsRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        *,
        section_id: str,
        book_id: str,
        ordinal: int,
        content: str,
        heading: str | None = None,
        heading_path: str = "",
        source_locator: str | None = None,
    ) -> SectionORM:
        section = SectionORM(
            id=section_id,
            book_id=book_id,
            ordinal=ordinal,
            heading=heading,
            heading_path=heading_path,
            content=content,
            source_locator=source_locator,
            created_at=datetime.utcnow(),
        )
        self.session.add(section)
        self.session.flush()
        return section

    def list_by_book(self, book_id: str, *, limit: int = 200, offset: int = 0) -> list[SectionORM]:
        return (
            self.session.query(SectionORM)
            .filter(SectionORM.book_id == book_id)
            .order_by(SectionORM.ordinal.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )
