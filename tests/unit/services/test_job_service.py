from __future__ import annotations

import pytest

from packages.core.models.enums import JobType
from packages.services.job_service import InvalidJobTransitionError, JobService
from packages.storage.db.session import get_session_factory, init_db


def test_job_service_transitions():
    init_db()
    session = get_session_factory()()
    service = JobService(session)

    job_id = service.create_job(job_type=JobType.INGEST, book_id="book-1", payload={"x": 1})

    started = service.start(job_id, step="fetch")
    assert started["status"] == "running"

    advanced = service.advance(job_id, step="snapshot", payload_patch={"snapshot": "ok"})
    assert advanced["current_step"] == "snapshot"
    assert advanced["payload"]["snapshot"] == "ok"

    finished = service.finish(job_id)
    assert finished["status"] == "completed"

    with pytest.raises(InvalidJobTransitionError):
        service.start(job_id, step="restart")

    session.close()
