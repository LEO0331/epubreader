from __future__ import annotations


def evaluate_retrieval(
    *,
    citations: list[dict[str, object]],
    min_required: int = 1,
) -> dict[str, object]:
    count = len(citations)
    with_chunk = sum(1 for c in citations if str(c.get("chunk_id", "")))
    return {
        "citation_count": count,
        "citations_with_chunk_id": with_chunk,
        "pass": count >= min_required and with_chunk == count,
    }
