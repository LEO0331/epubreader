from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from packages.core.config.loader import get_settings
from packages.core.models.enums import JobType
from packages.generation import ArtifactService
from packages.llm.router import get_default_llm_provider
from packages.services.job_service import JobService
from packages.storage.db.session import get_db_session

router = APIRouter(prefix="/books/{book_id}/artifacts", tags=["artifacts"])


class ArtifactBuildRequest(BaseModel):
    include_skill: bool = False


@router.post("/build")
def build_artifacts(
    book_id: str,
    payload: ArtifactBuildRequest,
    db: Session = Depends(get_db_session),
) -> dict[str, object]:
    settings = get_settings()
    jobs = JobService(db)
    job_id = jobs.create_job(
        job_type=JobType.ARTIFACT,
        book_id=book_id,
        payload={"include_skill": payload.include_skill},
    )
    jobs.start(job_id, step="artifact_generation")

    service = ArtifactService(
        db,
        data_root=settings.storage.data_dir,
        prompts_dir=str(Path("prompts").resolve()),
        provider=get_default_llm_provider(),
    )
    try:
        result = service.build_for_book(book_id=book_id, include_skill=payload.include_skill)
    except ValueError as exc:
        jobs.fail(job_id, message=str(exc))
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    jobs.finish(job_id, payload_patch={"artifacts": result["artifacts"]})
    result["job_id"] = job_id
    return result


@router.get("")
def list_artifacts(book_id: str, db: Session = Depends(get_db_session)) -> list[dict[str, object]]:
    settings = get_settings()
    service = ArtifactService(
        db,
        data_root=settings.storage.data_dir,
        prompts_dir=str(Path("prompts").resolve()),
        provider=get_default_llm_provider(),
    )
    return service.list_artifacts(book_id=book_id)


@router.get("/{artifact_type}")
def get_artifact(
    book_id: str,
    artifact_type: str,
    db: Session = Depends(get_db_session),
) -> dict[str, object]:
    settings = get_settings()
    service = ArtifactService(
        db,
        data_root=settings.storage.data_dir,
        prompts_dir=str(Path("prompts").resolve()),
        provider=get_default_llm_provider(),
    )
    artifact = service.get_artifact(book_id=book_id, artifact_type=artifact_type)
    if artifact is None:
        raise HTTPException(
            status_code=404,
            detail=f"Artifact not found for book={book_id}, type={artifact_type}",
        )
    return artifact
