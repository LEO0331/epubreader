from __future__ import annotations

from pathlib import Path

from packages.generation.artifact_service import ArtifactService
from packages.llm.router import EchoProvider
from packages.storage.db.session import get_session_factory, init_db
from packages.storage.repositories.books_repo import BooksRepository
from packages.storage.repositories.chunks_repo import ChunksRepository


def test_artifact_service_generates_summary_wiki_qa(tmp_path: Path):
    init_db()
    session = get_session_factory()()

    books = BooksRepository(session)
    chunks = ChunksRepository(session)

    book = books.create(
        book_id="book-art",
        source_type="uploaded_epub",
        source_ref="book.epub",
        status="chunked",
        language="en",
    )
    chunks.create(
        chunk_id="chk-1",
        book_id=book.id,
        section_id="sec-1",
        ordinal=0,
        text="Important content for generation.",
        metadata={"section_ordinal": "0"},
    )
    session.commit()

    service = ArtifactService(
        session,
        data_root=str(tmp_path),
        prompts_dir=str(Path("prompts").resolve()),
        provider=EchoProvider(),
    )

    result = service.build_for_book(book_id=book.id, include_skill=True)

    assert "summary" in result["artifacts"]
    assert "wiki" in result["artifacts"]
    assert "qa" in result["artifacts"]

    summary_path = Path(result["artifacts"]["summary"])
    assert summary_path.exists()

    session.close()
