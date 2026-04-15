from __future__ import annotations

from packages.evaluation import evaluate_generation_drift, evaluate_parse, evaluate_retrieval


def test_parse_eval_passes_for_non_empty_sections():
    result = evaluate_parse([{"heading": "h", "content": "x"}])
    assert result["pass"] is True


def test_retrieval_eval_requires_chunk_ids():
    result = evaluate_retrieval(citations=[{"chunk_id": "c1"}], min_required=1)
    assert result["pass"] is True


def test_generation_drift_ratio():
    result = evaluate_generation_drift(summary="abcd", answer="abcdefgh")
    assert result["pass"] is True
