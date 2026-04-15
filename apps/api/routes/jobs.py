from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from packages.services.job_service import JobNotFoundError, JobService
from packages.storage.db.session import get_db_session

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db_session)) -> dict[str, object]:
    service = JobService(db)
    try:
        return service.get_job(job_id)
    except JobNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
