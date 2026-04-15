from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from packages.chunking.semantic_chunker import SemanticChunker
from packages.chunking.structure_chunker import (
    ChunkOutput,
    ChunkPolicy,
    SectionInput,
    StructureChunker,
    word_count,
)
from packages.core.models.enums import ArtifactType, BookStatus
from packages.storage.repositories.artifacts_repo import ArtifactsRepository
from packages.storage.repositories.books_repo import BooksRepository
from packages.storage.repositories.chunks_repo import ChunksRepository
from packages.storage.repositories.sections_repo import SectionsRepository


class ChunkingService:
    def __init__(self, session: Session, data_root: str):
        self.session = session
        self.data_root = Path(data_root)
        self.books = BooksRepository(session)
        self.sections = SectionsRepository(session)
        self.chunks = ChunksRepository(session)
        self.artifacts = ArtifactsRepository(session)
        self.structure = StructureChunker(policy=ChunkPolicy())
        self.semantic = SemanticChunker(max_words=260, target_words=180)

    def chunk_book(self, *, book_id: str) -> dict[str, object]:
        book = self.books.get(book_id)
        if book is None:
            raise ValueError(f"Book not found: {book_id}")

        section_rows = self.sections.list_by_book(book_id, limit=100000, offset=0)
        section_payloads: list[SectionInput] = [
            {
                "id": row.id,
                "ordinal": row.ordinal,
                "heading": row.heading,
                "heading_path": [x for x in row.heading_path.split(" > ") if x.strip()],
                "content": row.content,
            }
            for row in section_rows
        ]

        structured = self.structure.chunk_sections(
            book_id=book_id,
            language=book.language,
            sections=section_payloads,
        )

        final_chunks: list[ChunkOutput] = []
        for chunk in structured:
            text = chunk["text"]
            if word_count(text) > self.structure.policy.max_words:
                section_ordinal = int(chunk["metadata"].get("section_ordinal", "0"))
                fallback = self.semantic.split_oversized_chunk(
                    book_id=book_id,
                    section_id=chunk["section_id"],
                    section_ordinal=section_ordinal,
                    text=text,
                    base_metadata=dict(chunk["metadata"]),
                )
                final_chunks.extend(fallback)
            else:
                final_chunks.append(chunk)

        for idx, chunk in enumerate(final_chunks):
            chunk["ordinal"] = idx

        self.chunks.delete_by_book(book_id)
        for item in final_chunks:
            self.chunks.create(
                chunk_id=item["id"],
                book_id=book_id,
                section_id=item["section_id"],
                ordinal=item["ordinal"],
                text=item["text"],
                metadata={str(k): str(v) for k, v in item["metadata"].items()},
            )

        normalized_dir = self.data_root / "normalized" / book_id
        normalized_dir.mkdir(parents=True, exist_ok=True)
        chunks_path = normalized_dir / "chunks.jsonl"
        with chunks_path.open("w", encoding="utf-8") as handle:
            for item in final_chunks:
                record = {
                    "id": item["id"],
                    "book_id": book_id,
                    "section_id": item["section_id"],
                    "ordinal": item["ordinal"],
                    "text": item["text"],
                    "metadata": item["metadata"],
                }
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")

        self.artifacts.create(
            artifact_id=str(uuid4()),
            book_id=book_id,
            artifact_type=ArtifactType.CHUNKS.value,
            path=str(chunks_path),
            metadata={"chunk_count": str(len(final_chunks))},
        )

        book.status = BookStatus.CHUNKED.value
        self.session.commit()

        return {
            "book_id": book_id,
            "chunk_count": len(final_chunks),
            "chunks_path": str(chunks_path),
        }
