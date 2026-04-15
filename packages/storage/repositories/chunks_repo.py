from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy.orm import Session

from packages.storage.db.models import ChunkORM


class ChunksRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        *,
        chunk_id: str,
        book_id: str,
        ordinal: int,
        text: str,
        metadata: dict[str, str],
        section_id: str | None = None,
    ) -> ChunkORM:
        chunk = ChunkORM(
            id=chunk_id,
            book_id=book_id,
            section_id=section_id,
            ordinal=ordinal,
            text=text,
            metadata_json=json.dumps(metadata),
            created_at=datetime.utcnow(),
        )
        self.session.add(chunk)
        self.session.flush()
        return chunk

    def list_by_book(self, book_id: str, *, limit: int = 100, offset: int = 0) -> list[ChunkORM]:
        return (
            self.session.query(ChunkORM)
            .filter(ChunkORM.book_id == book_id)
            .order_by(ChunkORM.ordinal.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )
