# Milestone 4 Implementation Notes

Milestone 4 covers TASK-023 through TASK-026.

## Completed deliverables
- LLM provider abstraction and Ollama integration:
  - `packages/llm/base.py`
  - `packages/llm/ollama_provider.py`
  - `packages/llm/router.py`
  - `packages/llm/smoke.py`
- Prompt loader and prompt files:
  - `packages/prompts/loader.py`
  - prompt files under `prompts/`:
    - `classify_genre.md`
    - `chunk_summary.md`
    - `wiki_transform.md`
    - `skill_extract.md`
    - `synthetic_qa.md`
    - `answer_with_citations.md`
- Artifact generators and orchestration:
  - `packages/generation/summary_generator.py`
  - `packages/generation/wiki_generator.py`
  - `packages/generation/skill_generator.py`
  - `packages/generation/qa_generator.py`
  - `packages/generation/artifact_service.py`
- Artifact API routes:
  - `POST /api/v1/books/{book_id}/artifacts/build`
  - `GET /api/v1/books/{book_id}/artifacts`
  - `GET /api/v1/books/{book_id}/artifacts/{artifact_type}`

## Sample progression updated
- `sample/miz-500/summary.md`
- `sample/miz-500/wiki.md`
- `sample/miz-500/qa.jsonl`
- `sample/miz-500/skill.md` (when skill generation is requested/eligible)

## Validation evidence
- `python3 -m ruff check .`
- `python3 -m mypy .`
- `python3 -m pytest`
