from __future__ import annotations

from packages.quality.quality_scoring import ParseQualityScoringService
from packages.storage.db.session import get_session_factory, init_db
from packages.storage.repositories.books_repo import BooksRepository
from packages.storage.repositories.sections_repo import SectionsRepository


def test_quality_scoring_persists_score():
    init_db()
    session = get_session_factory()()

    books = BooksRepository(session)
    sections = SectionsRepository(session)

    book = books.create(
        book_id="book-quality",
        source_type="uploaded_epub",
        source_ref="quality.epub",
        status="cleaned",
    )

    sections.create(
        section_id="sec-1",
        book_id=book.id,
        ordinal=0,
        heading="Intro",
        heading_path="Intro",
        content="This is useful and reasonably long content for quality scoring.",
    )
    sections.create(
        section_id="sec-2",
        book_id=book.id,
        ordinal=1,
        heading="Next",
        heading_path="Intro > Next",
        content="Another paragraph with enough text to avoid being classified as noise.",
    )
    session.commit()

    service = ParseQualityScoringService(session)
    metrics = service.score_book(book_id=book.id)

    assert metrics["overall"] > 0.0
    reloaded = books.get(book.id)
    assert reloaded is not None
    assert reloaded.parse_quality_score is not None

    session.close()
