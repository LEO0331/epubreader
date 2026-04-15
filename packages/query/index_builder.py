from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session

from packages.embeddings import EmbeddingRequest, get_default_embedding_provider
from packages.indexing import ChromaStore, collection_name_for_book
from packages.indexing.chroma_store import VectorRecord
from packages.storage.repositories.books_repo import BooksRepository
from packages.storage.repositories.chunks_repo import ChunksRepository


@dataclass(frozen=True)
class IndexBuildStats:
    book_id: str
    collection_name: str
    chunk_count: int


class IndexBuilder:
    def __init__(self, session: Session, data_root: str):
        self.session = session
        self.books = BooksRepository(session)
        self.chunks = ChunksRepository(session)
        self.embedder = get_default_embedding_provider()
        self.store = ChromaStore(persist_path=str(Path(data_root) / "chroma"))

    def build_for_books(self, *, book_ids: list[str]) -> list[IndexBuildStats]:
        stats: list[IndexBuildStats] = []
        for book_id in book_ids:
            book = self.books.get(book_id)
            if book is None:
                continue

            chunk_rows = self.chunks.list_by_book(book_id, limit=200000, offset=0)
            if not chunk_rows:
                continue

            texts = [row.text for row in chunk_rows]
            vectors = self.embedder.embed(EmbeddingRequest(texts=texts)).vectors
            collection_name = collection_name_for_book(book_id)

            self.store.get_or_create_collection(
                name=collection_name,
                metadata={
                    "book_id": book_id,
                    "scope": "book",
                    "strategy": "book_id_v1",
                },
            )
            records: list[VectorRecord] = []
            for idx, row in enumerate(chunk_rows):
                records.append(
                    {
                        "id": row.id,
                        "document": row.text,
                        "embedding": vectors[idx],
                        "metadata": {
                            "book_id": book_id,
                            "section_id": row.section_id or "",
                            "chunk_id": row.id,
                            "ordinal": str(row.ordinal),
                        },
                    }
                )
            self.store.upsert(collection_name=collection_name, records=records)
            self.books.update_status(book_id, "indexed")

            stats.append(
                IndexBuildStats(
                    book_id=book_id,
                    collection_name=collection_name,
                    chunk_count=len(chunk_rows),
                )
            )

        self.session.commit()
        return stats
