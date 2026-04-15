from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from packages.core.models.enums import ArtifactType


class Artifact(BaseModel):
    id: str
    book_id: str
    artifact_type: ArtifactType
    path: str
    metadata: dict[str, str] = Field(default_factory=dict)
    created_at: datetime
