from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from packages.core.models.enums import ArtifactType, BookStatus
from packages.parsing.epub_parser import parse_epub
from packages.parsing.html_parser import parse_html
from packages.storage.repositories.artifacts_repo import ArtifactsRepository
from packages.storage.repositories.books_repo import BooksRepository
from packages.storage.repositories.sections_repo import SectionsRepository


class ParsingService:
    def __init__(self, session: Session, data_root: str):
        self.session = session
        self.data_root = Path(data_root)
        self.books = BooksRepository(session)
        self.sections = SectionsRepository(session)
        self.artifacts = ArtifactsRepository(session)

    def parse_book(self, *, book_id: str) -> dict[str, object]:
        book = self.books.get(book_id)
        if book is None:
            raise ValueError(f"Book not found: {book_id}")
        if not book.raw_snapshot_path:
            raise ValueError(f"Book {book_id} has no raw snapshot path")

        snapshot_path = Path(book.raw_snapshot_path)
        parsed = self._parse_by_source(book.source_type, snapshot_path)

        normalized_dir = self.data_root / "normalized" / book_id
        normalized_dir.mkdir(parents=True, exist_ok=True)
        parsed_path = normalized_dir / "parsed.json"
        parsed_path.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")

        self.sections.delete_by_book(book_id)
        sections = parsed.get("sections", [])
        section_items = sections if isinstance(sections, list) else []
        for item in section_items:
            if not isinstance(item, dict):
                continue
            heading_path_raw = item.get("heading_path", [])
            heading_path_list = (
                [str(x) for x in heading_path_raw]
                if isinstance(heading_path_raw, list)
                else []
            )
            heading_path = " > ".join(heading_path_list)
            self.sections.create(
                section_id=str(uuid4()),
                book_id=book_id,
                ordinal=int(item.get("ordinal", 0)),
                heading=str(item.get("heading")) if item.get("heading") is not None else None,
                heading_path=heading_path,
                content=str(item.get("content", "")),
                source_locator=(
                    str(item.get("source_locator"))
                    if item.get("source_locator") is not None
                    else None
                ),
            )

        self.artifacts.create(
            artifact_id=str(uuid4()),
            book_id=book_id,
            artifact_type=ArtifactType.PARSED.value,
            path=str(parsed_path),
            metadata={"section_count": str(len(section_items))},
        )

        book.status = BookStatus.PARSED.value
        self.session.commit()
        return parsed

    def _parse_by_source(self, source_type: str, snapshot_path: Path) -> dict[str, object]:
        if source_type in {"epub_url", "uploaded_epub"}:
            return parse_epub(snapshot_path)
        if source_type == "miz_books":
            return parse_html(snapshot_path.read_bytes())
        raise ValueError(f"No parser for source_type={source_type}")
