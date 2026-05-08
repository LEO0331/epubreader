# Book QA Library System Design Deep Dive (English)

## 1) Scope and Goals
- Build a local-first, evidence-grounded QA system for books (EPUB/PDF/HTML-like sources).
- Keep parser-only operation possible when no LLM/API provider is available.
- Ensure ingestion-to-query workflow is inspectable, resumable where practical, and testable.
- Preserve source traceability: answers must be backed by retrieved chunks.

Non-goals (current version):
- Multi-tenant auth and billing.
- Cloud-native distributed job queue.
- Real-time collaborative editing.

## 2) High-Level Architecture
Layers:
1. API layer (`apps/api/routes/*`): thin HTTP routes and request/response schemas.
2. Service layer (`packages/services`, plus domain services in parsing/chunking/generation/query): orchestration and business rules.
3. Repository/data access layer (`packages/storage/repositories/*`): storage-specific CRUD/query operations.
4. Domain/model layer (`packages/core/models/*`, enums/settings): typed domain boundaries.
5. Processing modules:
   - Ingest adapters (`packages/ingest/adapters/*`)
   - Parsers (`packages/parsing/*`)
   - Cleaning (`packages/cleaning/*`)
   - Chunking (`packages/chunking/*`)
   - Generation (`packages/generation/*`)
   - Indexing/retrieval (`packages/indexing/*`, `packages/query/*`)
   - Exporters (`packages/exporters/*`)
6. Storage:
   - Relational metadata (SQLite via SQLAlchemy/Alembic).
   - Local filesystem artifacts (`data/raw`, `data/normalized`, `data/artifacts`, `data/exports`).
   - Vector store (Chroma persistent path).

Why this split:
- Keeps routes thin and business logic testable in pure Python.
- Allows parser/chunker/index/query evolution without route churn.
- Preserves local-first deployability (single machine, minimal infra).

## 3) End-to-End Data Flow
1. Ingest (`/api/v1/ingest/url|upload`) creates `Book` + `Job`, snapshots raw source.
2. Parsing service picks parser by source type (EPUB/HTML/PDF), persists `parsed.json` + `Section` rows.
3. Cleaning normalizes sections deterministically, saves cleaned artifact.
4. Chunking creates stable chunks with metadata; fallback semantic splitting for weak structure.
5. Optional generation creates summary/wiki/qa/skill artifacts.
6. Optional indexing embeds chunks into Chroma.
7. Query retrieves chunk evidence first, then synthesizes answer with citations.
8. Collections + export package outputs for filesystem/Obsidian/GitHub.

## 4) Core Data Structures and Why

### 4.1 Book/Section/Chunk normalized hierarchy
Chosen:
- `Book` (source-level entity)
- `Section` (ordered structural units)
- `Chunk` (retrieval unit with source metadata)

Why:
- Matches natural document hierarchy.
- Enables deterministic rebuild of chunks from sections.
- Supports evidence trace (book -> section -> chunk -> answer citation).

Alternatives:
- Flat paragraph table only:
  - Simpler writes, weaker structure fidelity and heading-aware chunking.
- Graph document model:
  - More flexible relationships, higher complexity and weaker local MVP ergonomics.

### 4.2 Relational metadata (SQLite + SQLAlchemy)
Chosen:
- SQLite for local portability and zero-ops startup.
- SQLAlchemy repositories for typed persistence boundaries.

Why:
- Easy local dev + tests.
- Sufficient for single-node metadata consistency.
- Migration support via Alembic.

Alternatives:
- Postgres first:
  - Better concurrency/scaling, heavier deployment burden for MVP.
- NoSQL document store:
  - Flexible schema, but weaker relational constraints for jobs/books/chunks.

### 4.3 Filesystem artifact storage
Chosen:
- Large/raw/derived payloads saved under `data/*`.

Why:
- Keeps DB lean (metadata + references, not huge blobs).
- Easy manual inspection/debugging.
- Cheap local persistence semantics.

Alternatives:
- Store everything in DB BLOBs:
  - Transactional, but heavier DB, harder manual inspection, larger backups.
- Object storage only:
  - Better cloud scale, conflicts with local-first and offline mode.

### 4.4 Vector store in Chroma (persistent local path)
Chosen:
- Chroma collections keyed by book/strategy.

Why:
- Lightweight local vector persistence.
- Works with local embedding providers.
- Supports retrieval preview and scoped query.

Alternatives:
- FAISS local index files:
  - Fast and portable, but fewer built-in metadata/filtering ergonomics.
- Postgres pgvector:
  - Strong production option, less local-zero-setup.

### 4.5 Job lifecycle as explicit state machine
Chosen:
- `Job` with status transitions (`create -> start -> advance -> finish/fail`).

Why:
- Auditable processing and resumability hooks.
- Better observability than ad-hoc task flags.
- Aligns with milestone-gated pipeline.

Alternatives:
- Fire-and-forget synchronous pipeline:
  - Simple but poor reliability and no checkpoint visibility.
- Full queue system (Celery/RQ):
  - Strong async scale, unnecessary infra overhead for local MVP.

### 4.6 Adapter registry + parser dispatch tables
Chosen:
- Adapter contract (`can_handle/fetch/extract_metadata/snapshot`) and parser routing by source type.

Why:
- Isolates source fetching from parsing logic.
- Extensible for new source types (PDF already added cleanly).

Alternatives:
- Monolithic ingest class with if/else blocks:
  - Faster initially, degrades maintainability quickly.

### 4.7 OCR fallback strategy (text-first then OCR)
Chosen:
- Extract native PDF text first; OCR low-text pages with thresholds/timeouts.

Why:
- Cost-efficient and faster on text PDFs.
- Improves scanned-PDF coverage without always paying OCR overhead.
- Graceful degradation when OCR runtime unavailable.

Alternatives:
- OCR every page always:
  - Better consistency for scans, much slower and heavier runtime.
- Cloud OCR APIs:
  - Higher quality possible, adds vendor lock-in, cost, and privacy concerns.

### 4.8 Export profile data structure (`basic|enhanced`)
Chosen:
- Backward-compatible enum-like profile in export request.

Why:
- No breaking API changes.
- Allows opt-in richer Obsidian frontmatter/tags/media handling.

Alternatives:
- New dedicated endpoint per export format:
  - More explicit, larger API surface and duplication.

## 5) Key Tradeoffs by Concern

### Simplicity vs Scalability
- Current design optimizes local simplicity first.
- Tradeoff: limited horizontal scale and multi-worker throughput.

### Determinism vs Model intelligence
- Deterministic cleaning/chunking first, model-assisted generation second.
- Tradeoff: may miss semantic nuance in deterministic steps, but easier QA/debug.

### Traceability vs storage size
- Rich metadata per chunk and stored artifacts increase footprint.
- Benefit: strong citation reliability and postmortem inspectability.

### Latency vs quality in query
- Retrieval-grounded answers reduce hallucination risk.
- Tradeoff: extra retrieval + citation assembly overhead.

## 6) Reliability and Safety Design Notes
- Request ID middleware + stable JSON errors for supportability.
- API key middleware option for non-local environments.
- URL ingestion protections (SSRF/sizing controls).
- Export path safety checks (stay under controlled export root).
- OCR guardrails (page/time limits, optional worker isolation in hardened mode).

## 7) Alternatives for Next Stage
1. Metadata DB: migrate SQLite -> Postgres for concurrent workloads.
2. Job execution: move to queue workers while preserving `JobService` contract.
3. Retrieval: hybrid BM25 + vector retrieval for recall robustness.
4. Model routing: provider-aware gateway with policy-based fallback.
5. Storage: optional object storage adapter for artifacts.

## 8) Deep-Dive Question Bank (with prepared answers)

Q1. Why not store full text only in vector DB and skip sections/chunks tables?
- Because vector DB is for retrieval, not canonical document lineage. We need deterministic provenance, reprocessing, and API inspection endpoints independent from embedding/index implementation.

Q2. Why does query require retrieved evidence before answering?
- This enforces grounded QA and reduces hallucination risk. It also provides auditable citations required by this project’s acceptance rules.

Q3. Why keep both filesystem artifacts and DB metadata?
- DB is optimized for query/filter/state; filesystem is optimized for large payload persistence and manual debug. Keeping paths in DB balances both.

Q4. How does parser mode remain useful without LLM/API keys?
- Ingest -> parse -> clean -> chunk flows are deterministic and local. Users still inspect structure quality and prepare data for later indexing/query.

Q5. Why not make everything asynchronous with a queue now?
- The current local-first objective prioritizes operability and low setup complexity. The explicit job lifecycle keeps an upgrade path to workers later.

Q6. How do you avoid brittle source-specific parsing logic?
- Source acquisition is isolated in adapters; content normalization is in parser modules with typed contracts. New sources add modules without changing core route contracts.

Q7. How is PDF OCR cost controlled?
- Text-first extraction, OCR thresholding, per-page and total timeouts, optional page caps, and graceful fallback when OCR runtime is absent.

Q8. What if a chunking strategy changes?
- Chunk IDs are stable for unchanged inputs under the same policy. Policy changes should be versioned and trigger re-chunk/re-index workflows.

Q9. Why Chroma and not pgvector today?
- Chroma has lower operational friction for local persistent vector storage. pgvector is a good production upgrade path once managed DB is justified.

Q10. Biggest current architecture risks?
- Local filesystem coupling in hosted ephemeral environments, single-node DB concurrency limits, and model-provider variability in artifact quality.

## 9) Suggested Deep-Dive Session Agenda
1. Domain model walkthrough (`Book/Section/Chunk/Job/Collection`).
2. Source adapter and parser orchestration internals.
3. Chunking policies and metadata guarantees.
4. Retrieval + citation contract and failure modes.
5. Export profiles and path/media safety.
6. Hardening roadmap (queue workers, DB migration, hybrid retrieval).
