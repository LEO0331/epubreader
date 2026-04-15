from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from packages.core.models.enums import BookStatus, SourceType


class Book(BaseModel):
    id: str
    title: str | None = None
    author: str | None = None
    language: str | None = None
    source_type: SourceType
    source_ref: str
    status: BookStatus = BookStatus.INGESTED
    parse_quality_score: float | None = Field(default=None, ge=0.0, le=1.0)
    created_at: datetime
    updated_at: datetime
