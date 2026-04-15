from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from packages.storage.db.models import CollectionBookORM, CollectionORM


class CollectionsRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, *, collection_id: str, name: str, collection_type: str) -> CollectionORM:
        collection = CollectionORM(
            id=collection_id,
            name=name,
            collection_type=collection_type,
            created_at=datetime.utcnow(),
        )
        self.session.add(collection)
        self.session.flush()
        return collection

    def add_book(self, *, collection_id: str, book_id: str) -> CollectionBookORM:
        link = CollectionBookORM(collection_id=collection_id, book_id=book_id)
        self.session.add(link)
        self.session.flush()
        return link

    def list_books(self, collection_id: str) -> list[str]:
        rows = (
            self.session.query(CollectionBookORM)
            .filter(CollectionBookORM.collection_id == collection_id)
            .all()
        )
        return [row.book_id for row in rows]
