# book-qa-library

`book-qa-library` is a local-first private library QA system for EPUB/web sources with grounded answers and citations.

## What This Project Includes
- **FastAPI backend** (`apps/api`) for ingestion, parsing pipeline, chunking, artifacts, indexing, query, and exports.
- **Next.js frontend** (`frontend`) for non-technical users.
- **Parser mode support** for partial online usage without LLM/API generation.

## Runtime Modes (Frontend)
- **API mode**: full workflow (ingest, inspect, artifacts, query, collections/export).
- **Parser mode**: ingest + inspect only (books, sections, chunks).

Parser mode disables artifact build/list actions, query actions, and collection export flows.

## Business Flow
1. User submits URL or EPUB upload.
2. Backend snapshots raw source.
3. Backend parses and cleans into ordered sections.
4. Backend chunks content with metadata.
5. Optional generation creates `summary/wiki/qa/skill` artifacts.
6. Optional indexing stores vectors in local Chroma.
7. Query retrieves chunk evidence and returns answer + citations.
8. Optional export writes markdown bundles for filesystem/Obsidian/GitHub.

## Project Tree
```text
book-qa-library/
├─ apps/
│  └─ api/
├─ packages/
│  ├─ core/
│  ├─ ingest/
│  ├─ parsing/
│  ├─ cleaning/
│  ├─ chunking/
│  ├─ llm/
│  ├─ embeddings/
│  ├─ indexing/
│  ├─ query/
│  ├─ generation/
│  ├─ services/
│  ├─ exporters/
│  ├─ evaluation/
│  └─ storage/
├─ frontend/               # Next.js 14 non-technical UI
├─ configs/
├─ prompts/
├─ migrations/
├─ tests/
├─ docs/
├─ sample/
└─ data/
```

## Local Setup (Backend)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,test]'
cp .env.example .env
make run
```

Health check:
```bash
curl -s http://127.0.0.1:8000/api/v1/health
```

## Local Setup (Frontend)
```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`.

## Online Deployment (Render + Vercel)

### 1) Deploy Backend to Render
- Create a **Web Service** from this GitHub repo.
- Runtime: Python.
- Build command:
```bash
pip install -e '.[dev,test]'
```
- Start command:
```bash
uvicorn apps.api.main:create_app --factory --host 0.0.0.0 --port $PORT
```
- Add persistent disk (recommended) at `/var/data`.
- Set env vars:
  - `APP_DATA_DIR=/var/data`
  - `APP_DATABASE_URL=sqlite:////var/data/app.db`
  - `APP_CONFIG_DIR=/opt/render/project/src/configs`
  - `APP_MODELS_PROFILE=api`
  - `APP_CORS_ALLOW_ORIGINS=https://<vercel-domain>,https://<optional-preview-domain>`

### 2) Deploy Frontend to Vercel
- Import the same GitHub repo in Vercel.
- Set **Root Directory** to `frontend`.
- Set env var:
  - `NEXT_PUBLIC_API_BASE_URL=https://<render-backend-domain>`
- Deploy.

### 3) GitHub Branch Flow
1. Push backend/frontend changes to your branch.
2. Merge to main.
3. Render and Vercel auto-deploy from GitHub.

## Partial Online Usage (No API Key / No Ollama)
Yes. If no generation API key is available, run in **parser mode**.
- Works: ingest, parse/clean results inspection, section/chunk inspection.
- Not available: artifact generation, query answering, collection export workflows that depend on generated content.

## API Endpoints
- `POST /api/v1/ingest/url`
- `POST /api/v1/ingest/upload`
- `POST /api/v1/ingest/text` (placeholder)
- `GET /api/v1/jobs/{job_id}`
- `GET /api/v1/books`
- `GET /api/v1/books/{book_id}`
- `GET /api/v1/books/{book_id}/sections`
- `GET /api/v1/books/{book_id}/chunks`
- `POST /api/v1/books/{book_id}/artifacts/build`
- `GET /api/v1/books/{book_id}/artifacts`
- `GET /api/v1/books/{book_id}/artifacts/{artifact_type}`
- `POST /api/v1/query/preview`
- `POST /api/v1/query`
- `POST /api/v1/collections`
- `GET /api/v1/collections`
- `GET /api/v1/collections/{collection_id}`
- `POST /api/v1/collections/{collection_id}/books`
- `DELETE /api/v1/collections/{collection_id}/books/{book_id}`
- `POST /api/v1/collections/{collection_id}/export`
