from __future__ import annotations


def evaluate_generation_drift(
    *,
    summary: str,
    answer: str,
    max_length_ratio: float = 2.5,
) -> dict[str, object]:
    summary_len = max(len(summary.strip()), 1)
    answer_len = len(answer.strip())
    ratio = answer_len / summary_len
    return {
        "summary_len": summary_len,
        "answer_len": answer_len,
        "length_ratio": round(ratio, 4),
        "pass": ratio <= max_length_ratio,
    }
