from __future__ import annotations

from sqlalchemy.orm import Session

from packages.storage.repositories.books_repo import BooksRepository
from packages.storage.repositories.sections_repo import SectionsRepository


class ParseQualityScoringService:
    def __init__(self, session: Session):
        self.session = session
        self.books = BooksRepository(session)
        self.sections = SectionsRepository(session)

    def score_book(self, *, book_id: str) -> dict[str, float]:
        book = self.books.get(book_id)
        if book is None:
            raise ValueError(f"Book not found: {book_id}")

        sections = self.sections.list_by_book(book_id, limit=100000, offset=0)
        if not sections:
            metrics = {
                "section_count_sanity": 0.0,
                "heading_density": 0.0,
                "text_density": 0.0,
                "noise_ratio": 1.0,
                "overall": 0.0,
            }
            book.parse_quality_score = metrics["overall"]
            self.session.commit()
            return metrics

        count = len(sections)
        heading_count = sum(1 for s in sections if s.heading)
        avg_chars = sum(len(s.content) for s in sections) / count
        short_count = sum(1 for s in sections if len(s.content.strip()) < 40)

        section_count_sanity = min(1.0, count / 20.0)
        heading_density = heading_count / count
        text_density = min(1.0, avg_chars / 600.0)
        noise_ratio = short_count / count

        overall = max(
            0.0,
            min(
                1.0,
                (0.35 * section_count_sanity)
                + (0.25 * heading_density)
                + (0.30 * text_density)
                + (0.10 * (1.0 - noise_ratio)),
            ),
        )

        metrics = {
            "section_count_sanity": round(section_count_sanity, 4),
            "heading_density": round(heading_density, 4),
            "text_density": round(text_density, 4),
            "noise_ratio": round(noise_ratio, 4),
            "overall": round(overall, 4),
        }

        book.parse_quality_score = metrics["overall"]
        self.session.commit()
        return metrics
