# Milestone 8 Implementation Notes

Milestone 8 covers TASK-030.

## Completed deliverables
- Evaluation modules:
  - `packages/evaluation/parse_eval.py`
  - `packages/evaluation/retrieval_eval.py`
  - `packages/evaluation/generation_drift.py`
- End-to-end test:
  - `tests/e2e/test_full_pipeline.py`
  - verifies ingest -> inspect -> chunk -> artifact build -> query with citations
- Docs updates:
  - `docs/local-workflow.md`
  - `docs/api-usage.md`
- Job/error reporting polish:
  - enhanced error payload includes request path and UTC timestamp

## Sample progression completed
`sample/miz-500/` now includes:
- source/parse/clean/chunk artifacts
- generation artifacts (`summary.md`, `wiki.md`, `qa.jsonl`, optional `skill.md`)
- query examples (`query_examples.json`)
- evaluation outputs (`eval_parse.json`, `eval_retrieval.json`, `eval_generation.json`)

## Validation evidence
- `python3 -m ruff check .`
- `python3 -m mypy .`
- `python3 -m pytest`
