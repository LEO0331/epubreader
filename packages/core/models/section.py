from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class Section(BaseModel):
    id: str
    book_id: str
    ordinal: int = Field(ge=0)
    heading: str | None = None
    heading_path: list[str] = Field(default_factory=list)
    content: str
    source_locator: str | None = None
    created_at: datetime
