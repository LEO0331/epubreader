from __future__ import annotations

from uuid import uuid4

from sqlalchemy.orm import Session

from packages.storage.repositories.collections_repo import CollectionsRepository


class CollectionService:
    def __init__(self, session: Session):
        self.session = session
        self.collections = CollectionsRepository(session)

    def create_collection(self, *, name: str, collection_type: str = "user") -> dict[str, object]:
        collection_id = str(uuid4())
        row = self.collections.create(
            collection_id=collection_id,
            name=name,
            collection_type=collection_type,
        )
        self.session.commit()
        return {
            "id": row.id,
            "name": row.name,
            "collection_type": row.collection_type,
            "created_at": row.created_at.isoformat(),
        }

    def list_collections(self) -> list[dict[str, object]]:
        rows = self.collections.list_collections()
        return [
            {
                "id": row.id,
                "name": row.name,
                "collection_type": row.collection_type,
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ]

    def add_book(self, *, collection_id: str, book_id: str) -> dict[str, str]:
        self.collections.add_book(collection_id=collection_id, book_id=book_id)
        self.session.commit()
        return {"collection_id": collection_id, "book_id": book_id}

    def remove_book(self, *, collection_id: str, book_id: str) -> dict[str, str]:
        self.collections.remove_book(collection_id=collection_id, book_id=book_id)
        self.session.commit()
        return {"collection_id": collection_id, "book_id": book_id}

    def list_books(self, *, collection_id: str) -> list[str]:
        return self.collections.list_books(collection_id)

    def get_collection(self, *, collection_id: str) -> dict[str, object] | None:
        row = self.collections.get(collection_id)
        if row is None:
            return None
        return {
            "id": row.id,
            "name": row.name,
            "collection_type": row.collection_type,
            "created_at": row.created_at.isoformat(),
            "book_ids": self.collections.list_books(collection_id),
        }
