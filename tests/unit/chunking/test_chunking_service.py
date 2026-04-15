from __future__ import annotations

from pathlib import Path

from packages.chunking.chunking_service import ChunkingService
from packages.storage.db.session import get_session_factory, init_db
from packages.storage.repositories.books_repo import BooksRepository
from packages.storage.repositories.sections_repo import SectionsRepository


def test_chunking_service_builds_chunks_and_artifact(tmp_path: Path):
    init_db()
    session = get_session_factory()()

    books = BooksRepository(session)
    sections = SectionsRepository(session)

    book = books.create(
        book_id="book-chunk",
        source_type="uploaded_epub",
        source_ref="book.epub",
        status="cleaned",
        language="en",
    )

    sections.create(
        section_id="sec-1",
        book_id=book.id,
        ordinal=0,
        heading="Chapter 1",
        heading_path="Chapter 1",
        content="Sentence one. Sentence two. Sentence three.",
    )
    session.commit()

    service = ChunkingService(session, data_root=str(tmp_path))
    result = service.chunk_book(book_id=book.id)

    assert result["chunk_count"] >= 1
    chunks_path = Path(str(result["chunks_path"]))
    assert chunks_path.exists()
    lines = chunks_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 1

    session.close()
