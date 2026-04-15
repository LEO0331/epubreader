from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from packages.core.models.enums import JobStatus, JobType


class Job(BaseModel):
    id: str
    job_type: JobType
    status: JobStatus
    book_id: str | None = None
    payload: dict[str, object] = Field(default_factory=dict)
    current_step: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
