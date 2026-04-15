# book-qa-library

`book-qa-library` is a local-first private library QA system.

## Architecture goals
- Local-first ingestion, parsing, chunking, indexing, and query workflows.
- Original chunks remain source-of-truth for retrieval and citations.
- Thin API routes with service-layer business logic.
- Deterministic pipeline stages first; model assistance is optional and scoped.

## Repository layout
- `apps/api/` FastAPI app, routers, middleware.
- `packages/core/` typed core modules (config, logging, domain models).
- `configs/` YAML configuration profiles.
- `docs/` implementation and design documentation.
- `data/` local runtime artifacts (raw, normalized, artifacts, vectors).
- `sample/` sample fixture outputs, including `sample/miz-500/`.

## Local setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev,test]
cp .env.example .env
make run
```

Health check:
```bash
curl -s http://127.0.0.1:8000/api/v1/health
```

## Milestone 1 API endpoints
- `POST /api/v1/ingest/url`
- `POST /api/v1/ingest/upload`
- `POST /api/v1/ingest/text` (placeholder)
- `GET /api/v1/jobs/{job_id}`
- `GET /api/v1/books`
