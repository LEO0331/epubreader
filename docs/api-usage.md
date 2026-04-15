# API Usage Notes

All API endpoints are under `/api/v1`.

## Core
- `GET /health`
- `GET /jobs/{job_id}`

## Ingestion and Inspection
- `POST /ingest/upload`
- `POST /ingest/url`
- `POST /ingest/text` (placeholder)
- `GET /books`
- `GET /books/{book_id}`
- `GET /books/{book_id}/sections`
- `GET /books/{book_id}/chunks`

## Artifacts
- `POST /books/{book_id}/artifacts/build`
- `GET /books/{book_id}/artifacts`
- `GET /books/{book_id}/artifacts/{artifact_type}`

## Query
- `POST /query/preview`
- `POST /query`

## Collections and Export
- `POST /collections`
- `GET /collections`
- `GET /collections/{collection_id}`
- `POST /collections/{collection_id}/books`
- `DELETE /collections/{collection_id}/books/{book_id}`
- `POST /collections/{collection_id}/export`
