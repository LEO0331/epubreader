# Local Workflow Guide

## Setup
1. Create and activate a virtual environment.
2. Install dependencies with `pip install -e '.[dev,test]'`.
3. Start the API with `make run`.

## Pipeline Walkthrough
1. Ingest a source (upload EPUB or URL).
2. Inspect parsed/cleaned sections.
3. Inspect generated chunks.
4. Build artifacts (`summary`, `wiki`, `qa`, optional `skill`).
5. Run retrieval preview and grounded query answer.
6. Optionally create collections and export markdown bundles.

## Key API Sequence
1. `POST /api/v1/ingest/upload`
2. `GET /api/v1/books/{book_id}/sections`
3. `GET /api/v1/books/{book_id}/chunks`
4. `POST /api/v1/books/{book_id}/artifacts/build`
5. `POST /api/v1/query/preview`
6. `POST /api/v1/query`

## Validation
- `python3 -m ruff check .`
- `python3 -m mypy .`
- `python3 -m pytest`
