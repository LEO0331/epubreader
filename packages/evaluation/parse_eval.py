from __future__ import annotations


def evaluate_parse(sections: list[dict[str, object]]) -> dict[str, object]:
    count = len(sections)
    non_empty = sum(1 for s in sections if str(s.get("content", "")).strip())
    heading_ratio = (
        sum(1 for s in sections if s.get("heading")) / count if count else 0.0
    )

    return {
        "section_count": count,
        "non_empty_sections": non_empty,
        "heading_ratio": round(heading_ratio, 4),
        "pass": count > 0 and non_empty == count,
    }
