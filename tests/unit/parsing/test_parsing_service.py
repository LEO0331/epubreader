from __future__ import annotations

from pathlib import Path

from packages.parsing.parsing_service import ParsingService
from packages.storage.db.session import get_session_factory, init_db
from packages.storage.repositories.books_repo import BooksRepository
from packages.storage.repositories.sections_repo import SectionsRepository


def test_parsing_service_routes_pdf_source_type(monkeypatch, tmp_path: Path):
    init_db()
    session = get_session_factory()()

    raw_path = tmp_path / "raw" / "book-1"
    raw_path.mkdir(parents=True, exist_ok=True)
    snapshot = raw_path / "source.pdf"
    snapshot.write_bytes(b"%PDF-1.4\n")

    books_repo = BooksRepository(session)
    book = books_repo.create(
        book_id="book-1",
        source_type="uploaded_pdf",
        source_ref="book.pdf",
        status="ingested",
    )
    books_repo.update_snapshot_path(book.id, str(snapshot))
    session.commit()

    monkeypatch.setattr(
        "packages.parsing.parsing_service.parse_pdf",
        lambda *args, **kwargs: {
            "metadata": {"title": "T", "author": "A", "language": None, "toc": []},
            "sections": [
                {
                    "ordinal": 0,
                    "heading": "Page 1",
                    "heading_path": ["Page 1"],
                    "content": "PDF section",
                    "source_locator": "page:1",
                }
            ],
        },
    )

    service = ParsingService(session, data_root=str(tmp_path))
    out = service.parse_book(book_id=book.id)

    assert out["sections"][0]["source_locator"] == "page:1"
    sections = SectionsRepository(session).list_by_book(book.id, limit=10, offset=0)
    assert len(sections) == 1

    parsed_file = tmp_path / "normalized" / book.id / "parsed.json"
    assert parsed_file.exists()

    session.close()
