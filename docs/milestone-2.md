# Milestone 2 Implementation Notes

Milestone 2 covers TASK-014 through TASK-019.

## Completed deliverables
- Parsers:
  - `packages/parsing/epub_parser.py`
  - `packages/parsing/html_parser.py`
- Parser orchestration:
  - `packages/parsing/parsing_service.py`
  - parsed artifact output under `data/normalized/<book_id>/parsed.json`
  - section persistence and replacement in DB
- Cleaning pipeline:
  - `packages/cleaning/rules.py`
  - `packages/cleaning/cleaning_service.py`
  - cleaned artifact output under `data/normalized/<book_id>/cleaned.json`
- Parse quality scoring:
  - `packages/quality/quality_scoring.py`
  - score persisted to `books.parse_quality_score`
- Book inspection API:
  - `GET /api/v1/books`
  - `GET /api/v1/books/{book_id}`
  - `GET /api/v1/books/{book_id}/sections`

## Sample progression updated
- `sample/miz-500/source_manifest.json`
- `sample/miz-500/parsed.json`
- `sample/miz-500/cleaned.json`

## Validation evidence
- `python3 -m ruff check .`
- `python3 -m mypy .`
- `python3 -m pytest`
