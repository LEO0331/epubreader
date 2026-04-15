from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from packages.cleaning.rules import is_boilerplate, normalize_text, repair_heading
from packages.core.models.enums import ArtifactType, BookStatus
from packages.storage.repositories.artifacts_repo import ArtifactsRepository
from packages.storage.repositories.books_repo import BooksRepository
from packages.storage.repositories.sections_repo import SectionsRepository


class CleaningService:
    def __init__(self, session: Session, data_root: str):
        self.session = session
        self.data_root = Path(data_root)
        self.books = BooksRepository(session)
        self.sections = SectionsRepository(session)
        self.artifacts = ArtifactsRepository(session)

    def clean_book(self, *, book_id: str) -> dict[str, object]:
        book = self.books.get(book_id)
        if book is None:
            raise ValueError(f"Book not found: {book_id}")

        rows = self.sections.list_by_book(book_id, limit=100000, offset=0)
        cleaned_sections: list[dict[str, object]] = []

        for row in rows:
            content = normalize_text(row.content)
            if is_boilerplate(content):
                continue

            heading = repair_heading(row.heading, content)
            heading_path_list = [
                normalize_text(x)
                for x in row.heading_path.split(" > ")
                if x.strip()
            ]
            if heading and (not heading_path_list or heading_path_list[-1] != heading):
                heading_path_list.append(heading)

            cleaned_sections.append(
                {
                    "ordinal": len(cleaned_sections),
                    "heading": heading,
                    "heading_path": heading_path_list,
                    "content": content,
                    "source_locator": row.source_locator,
                }
            )

        normalized_dir = self.data_root / "normalized" / book_id
        normalized_dir.mkdir(parents=True, exist_ok=True)
        cleaned_path = normalized_dir / "cleaned.json"
        cleaned_payload: dict[str, object] = {"book_id": book_id, "sections": cleaned_sections}
        cleaned_path.write_text(
            json.dumps(cleaned_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.sections.delete_by_book(book_id)
        for item in cleaned_sections:
            heading_raw = item.get("heading")
            heading = str(heading_raw) if heading_raw is not None else None
            ordinal_raw = item.get("ordinal", 0)
            ordinal = ordinal_raw if isinstance(ordinal_raw, int) else int(str(ordinal_raw))
            heading_path_raw = item.get("heading_path")
            heading_path_list = (
                [str(x) for x in heading_path_raw] if isinstance(heading_path_raw, list) else []
            )
            self.sections.create(
                section_id=str(uuid4()),
                book_id=book_id,
                ordinal=ordinal,
                heading=heading,
                heading_path=" > ".join(heading_path_list),
                content=str(item.get("content", "")),
                source_locator=(
                    str(item.get("source_locator")) if item.get("source_locator") else None
                ),
            )

        self.artifacts.create(
            artifact_id=str(uuid4()),
            book_id=book_id,
            artifact_type=ArtifactType.CLEANED.value,
            path=str(cleaned_path),
            metadata={"section_count": str(len(cleaned_sections))},
        )

        book.status = BookStatus.CLEANED.value
        self.session.commit()
        return cleaned_payload
