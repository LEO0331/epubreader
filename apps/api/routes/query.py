from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from packages.core.config.loader import get_settings
from packages.query import QueryEngine
from packages.storage.db.session import get_db_session

router = APIRouter(prefix="/query", tags=["query"])


class QueryPreviewRequest(BaseModel):
    question: str = Field(min_length=1)
    book_ids: list[str] | None = None
    collection_id: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    book_ids: list[str] | None = None
    collection_id: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)


@router.post("/preview")
def query_preview(
    payload: QueryPreviewRequest,
    db: Session = Depends(get_db_session),
) -> dict[str, object]:
    settings = get_settings()
    engine = QueryEngine(
        session=db,
        data_root=settings.storage.data_dir,
        prompts_dir=str(Path("prompts").resolve()),
    )
    return engine.preview(
        question=payload.question,
        book_ids=payload.book_ids,
        collection_id=payload.collection_id,
        top_k=payload.top_k,
    )


@router.post("")
def query_answer(payload: QueryRequest, db: Session = Depends(get_db_session)) -> dict[str, object]:
    settings = get_settings()
    engine = QueryEngine(
        session=db,
        data_root=settings.storage.data_dir,
        prompts_dir=str(Path("prompts").resolve()),
    )
    try:
        return engine.answer(
            question=payload.question,
            book_ids=payload.book_ids,
            collection_id=payload.collection_id,
            top_k=payload.top_k,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
