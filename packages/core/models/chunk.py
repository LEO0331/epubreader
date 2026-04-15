from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    id: str
    book_id: str
    section_id: str | None = None
    ordinal: int = Field(ge=0)
    text: str
    metadata: dict[str, str] = Field(default_factory=dict)
    created_at: datetime
