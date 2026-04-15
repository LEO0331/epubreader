# Milestone 3 Implementation Notes

Milestone 3 covers TASK-020 through TASK-022.

## Completed deliverables
- Structure-first chunker:
  - `packages/chunking/structure_chunker.py`
  - deterministic stable chunk IDs
  - metadata includes book/section/chapter/heading/heading_path/language
- Semantic fallback + chunking service:
  - `packages/chunking/semantic_chunker.py`
  - `packages/chunking/chunking_service.py`
  - chunk persistence and rebuild behavior (delete + recreate per book)
  - `data/normalized/<book_id>/chunks.jsonl` generation
- Chunk inspection API:
  - `GET /api/v1/books/{book_id}/chunks`
  - pagination support (`limit`, `offset`)
  - optional `section_id` filter

## Sample progression updated
- `sample/miz-500/chunks.jsonl`

## Validation evidence
- `python3 -m ruff check .`
- `python3 -m mypy .`
- `python3 -m pytest`
