# Milestone 7 Implementation Notes

Milestone 7 covers TASK-029.

## Completed deliverables
- Collection service and repository integration:
  - `packages/services/collection_service.py`
  - extended `packages/storage/repositories/collections_repo.py`
- Collection routes:
  - `POST /api/v1/collections`
  - `GET /api/v1/collections`
  - `GET /api/v1/collections/{collection_id}`
  - `POST /api/v1/collections/{collection_id}/books`
  - `DELETE /api/v1/collections/{collection_id}/books/{book_id}`
- Scoped querying:
  - `POST /api/v1/query` and `/query/preview` now support `collection_id`
  - query scope can be narrowed by explicit `book_ids` or collection membership
- Exporters:
  - filesystem exporter (`packages/exporters/filesystem_exporter.py`)
  - Obsidian exporter (`packages/exporters/obsidian_exporter.py`)
  - GitHub exporter (`packages/exporters/github_exporter.py`)
  - export route: `POST /api/v1/collections/{collection_id}/export`

## Validation evidence
- collection scope query integration test
- export route test
- `python3 -m ruff check .`
- `python3 -m mypy .`
- `python3 -m pytest`
