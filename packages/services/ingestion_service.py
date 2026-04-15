from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from packages.chunking import ChunkingService
from packages.cleaning import CleaningService
from packages.core.models.enums import ArtifactType, BookStatus, JobType
from packages.ingest.adapters import (
    AdapterRegistry,
    EpubUrlAdapter,
    MizBooksAdapter,
    UploadedEpubAdapter,
)
from packages.parsing import ParsingService
from packages.quality import ParseQualityScoringService
from packages.services.job_service import JobService
from packages.storage.repositories.artifacts_repo import ArtifactsRepository
from packages.storage.repositories.books_repo import BooksRepository


class IngestionService:
    def __init__(self, session: Session, data_root: str):
        self.session = session
        self.books_repo = BooksRepository(session)
        self.artifacts_repo = ArtifactsRepository(session)
        self.jobs = JobService(session)
        self.registry = AdapterRegistry(
            adapters=[
                EpubUrlAdapter(),
                UploadedEpubAdapter(),
                MizBooksAdapter(),
            ]
        )
        self.raw_root = Path(data_root) / "raw"
        self.parsing = ParsingService(session, data_root=data_root)
        self.cleaning = CleaningService(session, data_root=data_root)
        self.quality = ParseQualityScoringService(session)
        self.chunking = ChunkingService(session, data_root=data_root)

    def ingest_url(self, *, source_type: str, url: str) -> dict[str, str]:
        book_id = str(uuid4())
        book = self.books_repo.create(
            book_id=book_id,
            source_type=source_type,
            source_ref=url,
            status=BookStatus.INGESTED.value,
        )

        job_id = self.jobs.create_job(
            job_type=JobType.INGEST,
            book_id=book.id,
            payload={"source_type": source_type, "source_ref": url},
        )
        self.jobs.start(job_id, step="fetch_source")

        adapter = self.registry.select(source_type=source_type, source_ref=url)
        payload = adapter.fetch(source_ref=url)
        snapshot_path = adapter.snapshot(book_id=book.id, payload=payload, raw_root=self.raw_root)

        self.books_repo.update_snapshot_path(book.id, str(snapshot_path))
        self.artifacts_repo.create(
            artifact_id=str(uuid4()),
            book_id=book.id,
            artifact_type=ArtifactType.SOURCE_MANIFEST.value,
            path=str(snapshot_path.parent / "source_manifest.json"),
            metadata={"source_type": source_type, "snapshot_path": str(snapshot_path)},
        )

        manifest_path = snapshot_path.parent / "source_manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "book_id": book.id,
                    "source_type": source_type,
                    "source_ref": url,
                    "snapshot_path": str(snapshot_path),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        self.jobs.finish(
            job_id,
            payload_patch={
                "snapshot_path": str(snapshot_path),
                "source_metadata": adapter.extract_metadata(payload),
            },
        )

        self.parsing.parse_book(book_id=book.id)
        self.cleaning.clean_book(book_id=book.id)
        self.quality.score_book(book_id=book.id)
        self.chunking.chunk_book(book_id=book.id)

        self.session.commit()
        return {"book_id": book.id, "job_id": job_id}

    def ingest_upload(self, *, filename: str, upload_bytes: bytes) -> dict[str, str]:
        book_id = str(uuid4())
        book = self.books_repo.create(
            book_id=book_id,
            source_type="uploaded_epub",
            source_ref=filename,
            status=BookStatus.INGESTED.value,
            title=filename,
        )

        job_id = self.jobs.create_job(
            job_type=JobType.INGEST,
            book_id=book.id,
            payload={"source_type": "uploaded_epub", "source_ref": filename},
        )
        self.jobs.start(job_id, step="save_upload")

        adapter = self.registry.select(source_type="uploaded_epub", source_ref=filename)
        payload = adapter.fetch(source_ref=filename, upload_bytes=upload_bytes)
        snapshot_path = adapter.snapshot(book_id=book.id, payload=payload, raw_root=self.raw_root)

        self.books_repo.update_snapshot_path(book.id, str(snapshot_path))

        self.jobs.finish(
            job_id,
            payload_patch={
                "snapshot_path": str(snapshot_path),
                "source_metadata": adapter.extract_metadata(payload),
            },
        )

        self.parsing.parse_book(book_id=book.id)
        self.cleaning.clean_book(book_id=book.id)
        self.quality.score_book(book_id=book.id)
        self.chunking.chunk_book(book_id=book.id)

        self.session.commit()
        return {"book_id": book.id, "job_id": job_id}
