from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy.orm import Session

from packages.storage.db.models import QueryLogORM


class QueriesRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        *,
        query_id: str,
        question: str,
        book_scope: list[str],
        response_preview: str | None,
    ) -> QueryLogORM:
        query = QueryLogORM(
            id=query_id,
            question=question,
            book_scope=json.dumps(book_scope),
            response_preview=response_preview,
            created_at=datetime.utcnow(),
        )
        self.session.add(query)
        self.session.flush()
        return query
