from __future__ import annotations

import json

from sqlalchemy.orm import Session

from packages.storage.db.models import JobORM


class JobsRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        *,
        job_id: str,
        job_type: str,
        status: str,
        book_id: str | None,
        payload: dict[str, object],
        current_step: str | None = None,
    ) -> JobORM:
        job = JobORM(
            id=job_id,
            job_type=job_type,
            status=status,
            book_id=book_id,
            payload_json=json.dumps(payload),
            current_step=current_step,
        )
        self.session.add(job)
        self.session.flush()
        return job

    def get(self, job_id: str) -> JobORM | None:
        return self.session.get(JobORM, job_id)

    def update(
        self,
        job_id: str,
        *,
        status: str | None = None,
        current_step: str | None = None,
        error_message: str | None = None,
        payload: dict[str, object] | None = None,
    ) -> JobORM | None:
        job = self.get(job_id)
        if job is None:
            return None

        if status is not None:
            job.status = status
        if current_step is not None:
            job.current_step = current_step
        if error_message is not None:
            job.error_message = error_message
        if payload is not None:
            job.payload_json = json.dumps(payload)

        self.session.flush()
        return job
