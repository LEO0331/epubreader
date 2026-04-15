# Milestone 5 Implementation Notes

Milestone 5 covers TASK-027.

## Completed deliverables
- Embedding abstraction and local provider hook:
  - `packages/embeddings/base.py`
  - `packages/embeddings/local_provider.py`
  - `packages/embeddings/router.py`
- Chroma vector store wrapper:
  - `packages/indexing/chroma_store.py`
  - collection naming strategy via `collection_name_for_book(book_id)`
  - operations:
    - create/open collection
    - upsert vectors/documents/metadata
    - query by embedding
    - list collections
    - delete collection
- Public module exports:
  - `packages/embeddings/__init__.py`
  - `packages/indexing/__init__.py`

## Validation evidence
- persistence across restarts verified in tests
- vector upsert + retrieval verified in tests
- collection metadata preservation verified in tests
- `python3 -m ruff check .`
- `python3 -m mypy .`
- `python3 -m pytest`
