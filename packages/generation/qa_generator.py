from __future__ import annotations

import json

from packages.llm.base import LLMProvider, LLMProviderError, LLMRequest
from packages.prompts.loader import PromptLoader


def generate_synthetic_qa(
    *,
    provider: LLMProvider,
    prompt_loader: PromptLoader,
    chunk_records: list[dict[str, object]],
) -> dict[str, object]:
    evidence = "\n".join(f"[{row['id']}] {str(row['text'])[:300]}" for row in chunk_records[:12])
    prompt = prompt_loader.load("synthetic_qa", variables={"content": evidence})

    try:
        response = provider.generate(
            LLMRequest(prompt=prompt["content"], temperature=0.2, max_tokens=900)
        )
        qa_items = _parse_jsonl_or_fallback(response.text, chunk_records)
    except LLMProviderError:
        qa_items = _fallback_qa(chunk_records)

    return {
        "items": qa_items,
        "prompt_name": prompt["name"],
        "prompt_version": prompt["version"],
    }


def _parse_jsonl_or_fallback(
    raw: str,
    chunk_records: list[dict[str, object]],
) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        q = data.get("question")
        a = data.get("answer")
        c = data.get("citation")
        if isinstance(q, str) and isinstance(a, str):
            citation = c if isinstance(c, str) else ""
            items.append({"question": q, "answer": a, "citation": citation})
    return items or _fallback_qa(chunk_records)


def _fallback_qa(chunk_records: list[dict[str, object]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in chunk_records[:5]:
        text = str(row["text"])
        out.append(
            {
                "question": f"What does chunk {row['id']} discuss?",
                "answer": text[:220],
                "citation": str(row["id"]),
            }
        )
    return out
