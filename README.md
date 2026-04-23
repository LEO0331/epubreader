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

## Local Ollama Setup (For AI Features)
If you want artifact generation and Q&A locally, run Ollama:

1. Install Ollama from [ollama.com](https://ollama.com/).
2. Start Ollama:
```bash
ollama serve
```
3. Pull a model (example):
```bash
ollama pull llama3.1
```
4. Ensure config uses local profile (`configs/models.local.yaml`):
```yaml
llm:
  provider: ollama
  model: llama3.1
  timeout_seconds: 60
```
5. Ensure backend uses local models profile:
```bash
APP_MODELS_PROFILE=local
```

Without Ollama, parser-only features still work (ingest/parse/chunk inspection), but AI generation/query features will be limited.

## PDF + OCR Setup (Mandarin/English)
PDF ingest is supported via the same ingest endpoints.

### Install system packages (Linux / Render-like)
- `tesseract-ocr`
- `tesseract-ocr-chi-tra`
- `tesseract-ocr-eng`
- `poppler-utils`

### Configure OCR defaults
```bash
APP_OCR_ENABLED=true
APP_OCR_LANGS=chi_tra+eng
APP_OCR_MIN_TEXT_CHARS=80
# optional custom binary path
APP_OCR_TESSERACT_CMD=
# optional hardening limits (0 = disabled)
APP_OCR_MAX_PAGES=0
APP_OCR_PAGE_TIMEOUT_SECONDS=0
APP_OCR_TOTAL_TIMEOUT_SECONDS=0
APP_OCR_ISOLATE_WORKER=false
# optional URL ingestion host allowlist mode
APP_INGEST_HOST_ALLOWLIST_ENABLED=false
APP_INGEST_HOST_ALLOWLIST=
```

### OCR behavior
- Parser extracts embedded PDF text first.
- If a page has very little text (`APP_OCR_MIN_TEXT_CHARS`), OCR fallback is attempted.
- If OCR runtime is unavailable, parsing continues with embedded-text extraction (graceful degrade), and OCR availability is marked in parsed metadata.
- Optional hardening:
  - `APP_OCR_MAX_PAGES`, `APP_OCR_PAGE_TIMEOUT_SECONDS`, `APP_OCR_TOTAL_TIMEOUT_SECONDS` limit OCR workload.
  - `APP_OCR_ISOLATE_WORKER=true` runs OCR in a subprocess per page for safer isolation.
  - `APP_INGEST_HOST_ALLOWLIST_ENABLED=true` + `APP_INGEST_HOST_ALLOWLIST=example.com,cdn.example.com` restrict URL ingest hosts.

All hardening controls above are opt-in and disabled by default, so existing local and web deployments keep current behavior unless explicitly enabled.

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
  - `APP_API_KEY=<strong-random-value>` (optional but recommended for public deployments)
  - `APP_INGEST_MAX_BYTES=52428800` (optional upload/fetch size guard)
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

### 4) Lighthouse Deployment CI (Frontend)
- Workflow file: `.github/workflows/lighthouse-deployment.yml`
- Configure repository variable or secret:
  - `LIGHTHOUSE_DEPLOYMENT_URL=https://<your-vercel-domain>`
- The workflow audits deployed pages and enforces minimum scores:
  - Performance >= 90
  - Accessibility >= 90
  - Best Practices >= 90
  - SEO >= 90
- If `LIGHTHOUSE_DEPLOYMENT_URL` is not configured yet, the workflow exits cleanly without failing.

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

If `APP_API_KEY` is configured, include `X-API-Key: <value>` on all API requests except health checks.
In non-local environments (`APP_ENV` not `local/dev/test`), `APP_API_KEY` is required.

## User Flow (API Order)
Use this order when calling APIs manually (Postman/curl/frontend).

1. Health check
```http
GET /api/v1/health
```

2. Ingest source (choose one)
```http
POST /api/v1/ingest/upload
POST /api/v1/ingest/url
```
Examples:
- URL: `.epub`, `.pdf`, or supported `miz_books` page URL
- Upload: `.epub` or `.pdf`
Sample requests:
```bash
# PDF URL (auto-detected as pdf_url)
curl -X POST "$BASE_URL/api/v1/ingest/url" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"url":"https://example.com/book.pdf"}'

# Uploaded PDF (auto-detected as uploaded_pdf from filename)
curl -X POST "$BASE_URL/api/v1/ingest/upload" \
  -H "X-API-Key: $API_KEY" \
  -F "file=@/absolute/path/book.pdf"
```
Response returns:
- `book_id`
- `job_id`

3. Check ingest job status
```http
GET /api/v1/jobs/{job_id}
```

4. Inspect parsed content
```http
GET /api/v1/books/{book_id}
GET /api/v1/books/{book_id}/sections
GET /api/v1/books/{book_id}/chunks
```

5. Build artifacts (API mode)
```http
POST /api/v1/books/{book_id}/artifacts/build
GET /api/v1/books/{book_id}/artifacts
GET /api/v1/books/{book_id}/artifacts/{artifact_type}
```

6. Ask questions with evidence (API mode)
```http
POST /api/v1/query/preview
POST /api/v1/query
```
Use `book_ids` or `collection_id` in request body.

7. Collections + export (API mode)
```http
POST /api/v1/collections
POST /api/v1/collections/{collection_id}/books
POST /api/v1/collections/{collection_id}/export
```
Optional:
```http
GET /api/v1/collections
GET /api/v1/collections/{collection_id}
DELETE /api/v1/collections/{collection_id}/books/{book_id}
```

## Postman Collection
- Import book-qa-library.postman_collection.json
- Set collection variables:
  - `baseUrl` (e.g. `http://127.0.0.1:8000` or your Render URL)
  - `apiKey` (only if backend auth is enabled)
  - `bookId`, `jobId`, `collectionId` as needed after creating resources

## Test Coverage
Backend coverage is measured for `apps` + `packages` and enforced at **85% minimum**.

Run coverage locally:
```bash
make coverage
```
