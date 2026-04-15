from __future__ import annotations

import json
from uuid import uuid4

from sqlalchemy.orm import Session

from packages.core.models.enums import JobStatus, JobType
from packages.storage.repositories.jobs_repo import JobsRepository

_ALLOWED_TRANSITIONS: dict[JobStatus, set[JobStatus]] = {
    JobStatus.PENDING: {JobStatus.RUNNING, JobStatus.FAILED},
    JobStatus.RUNNING: {JobStatus.COMPLETED, JobStatus.FAILED},
    JobStatus.FAILED: set(),
    JobStatus.COMPLETED: set(),
}


class InvalidJobTransitionError(ValueError):
    pass


class JobNotFoundError(ValueError):
    pass


class JobService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = JobsRepository(session)

    def create_job(
        self,
        *,
        job_type: JobType,
        book_id: str | None,
        payload: dict[str, object] | None = None,
    ) -> str:
        job_id = str(uuid4())
        self.repo.create(
            job_id=job_id,
            job_type=job_type.value,
            status=JobStatus.PENDING.value,
            book_id=book_id,
            payload=payload or {},
        )
        self.session.commit()
        return job_id

    def get_job(self, job_id: str) -> dict[str, object]:
        job = self.repo.get(job_id)
        if job is None:
            raise JobNotFoundError(f"Job not found: {job_id}")

        return {
            "id": job.id,
            "job_type": job.job_type,
            "status": job.status,
            "book_id": job.book_id,
            "payload": json.loads(job.payload_json),
            "current_step": job.current_step,
            "error_message": job.error_message,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat(),
        }

    def start(self, job_id: str, *, step: str) -> dict[str, object]:
        return self._transition(job_id, to_status=JobStatus.RUNNING, step=step)

    def advance(
        self,
        job_id: str,
        *,
        step: str,
        payload_patch: dict[str, object] | None = None,
    ) -> dict[str, object]:
        job = self.repo.get(job_id)
        if job is None:
            raise JobNotFoundError(f"Job not found: {job_id}")
        if JobStatus(job.status) is not JobStatus.RUNNING:
            raise InvalidJobTransitionError("Can only advance running jobs")

        payload = json.loads(job.payload_json)
        if payload_patch:
            payload.update(payload_patch)

        self.repo.update(job_id, current_step=step, payload=payload)
        self.session.commit()
        return self.get_job(job_id)

    def fail(self, job_id: str, *, message: str) -> dict[str, object]:
        return self._transition(job_id, to_status=JobStatus.FAILED, error_message=message)

    def finish(
        self,
        job_id: str,
        *,
        payload_patch: dict[str, object] | None = None,
    ) -> dict[str, object]:
        job = self.repo.get(job_id)
        if job is None:
            raise JobNotFoundError(f"Job not found: {job_id}")

        payload = json.loads(job.payload_json)
        if payload_patch:
            payload.update(payload_patch)

        updated = self._transition(job_id, to_status=JobStatus.COMPLETED)
        self.repo.update(job_id, payload=payload)
        self.session.commit()
        return self.get_job(str(updated["id"]))

    def _transition(
        self,
        job_id: str,
        *,
        to_status: JobStatus,
        step: str | None = None,
        error_message: str | None = None,
    ) -> dict[str, object]:
        job = self.repo.get(job_id)
        if job is None:
            raise JobNotFoundError(f"Job not found: {job_id}")

        current = JobStatus(job.status)
        if to_status not in _ALLOWED_TRANSITIONS[current]:
            raise InvalidJobTransitionError(
                f"Invalid transition {current.value} -> {to_status.value}"
            )

        self.repo.update(
            job_id,
            status=to_status.value,
            current_step=step,
            error_message=error_message,
        )
        self.session.commit()
        return self.get_job(job_id)
