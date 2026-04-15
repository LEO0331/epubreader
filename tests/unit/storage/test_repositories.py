from __future__ import annotations

from packages.storage.db.session import get_session_factory, init_db
from packages.storage.repositories.books_repo import BooksRepository
from packages.storage.repositories.jobs_repo import JobsRepository


def test_books_and_jobs_repositories_roundtrip():
    init_db()
    session = get_session_factory()()

    books = BooksRepository(session)
    jobs = JobsRepository(session)

    book = books.create(
        book_id="book-1",
        source_type="uploaded_epub",
        source_ref="book.epub",
        status="ingested",
    )
    job = jobs.create(
        job_id="job-1",
        job_type="ingest",
        status="pending",
        book_id=book.id,
        payload={"k": "v"},
    )
    session.commit()

    fetched_book = books.get(book.id)
    fetched_job = jobs.get(job.id)

    assert fetched_book is not None
    assert fetched_book.source_ref == "book.epub"
    assert fetched_job is not None
    assert fetched_job.status == "pending"

    session.close()
