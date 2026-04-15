# Milestone 1 Implementation Notes

Milestone 1 covers TASK-006 through TASK-013.

## Completed deliverables
- Core domain entities in `packages/core/models/`:
  - `Book`, `Section`, `Chunk`, `Artifact`, `Job`, `Collection`
  - enums for statuses, source types, and artifact/job categories
- Database and migrations:
  - SQLAlchemy base/session modules
  - ORM models for books, sections, chunks, artifacts, jobs, collections, queries
  - Alembic setup with initial migration (`0001_initial_schema`)
- Repository layer:
  - `books_repo.py`, `jobs_repo.py`, `chunks_repo.py`, `artifacts_repo.py`, `queries_repo.py`, `collections_repo.py`
- Job lifecycle service:
  - `JobService` with guarded transitions and step tracking
- Source adapter abstraction and implementations:
  - adapter contract and registry
  - `epub_url`, `uploaded_epub`, `miz_books` adapters
- Ingestion API entrypoints:
  - `POST /api/v1/ingest/url`
  - `POST /api/v1/ingest/upload`
  - `POST /api/v1/ingest/text` placeholder
  - `GET /api/v1/jobs/{job_id}`

## Validation evidence
- `python3 -m ruff check .`
- `python3 -m mypy .`
- `python3 -m pytest`
- `python3 -m alembic -c alembic.ini upgrade head`
- `python3 -m alembic -c alembic.ini downgrade base`
- `python3 -m alembic -c alembic.ini upgrade head`

All commands completed successfully.
