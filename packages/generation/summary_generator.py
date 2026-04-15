from __future__ import annotations

from packages.llm.base import LLMProvider, LLMProviderError, LLMRequest
from packages.prompts.loader import PromptLoader


def generate_summary(
    *,
    provider: LLMProvider,
    prompt_loader: PromptLoader,
    chunk_texts: list[str],
) -> dict[str, str]:
    merged = "\n\n".join(chunk_texts[:10]).strip()
    prompt = prompt_loader.load("chunk_summary", variables={"content": merged})

    try:
        response = provider.generate(
            LLMRequest(prompt=prompt["content"], temperature=0.0, max_tokens=700)
        )
        text = response.text.strip()
    except LLMProviderError:
        text = _deterministic_summary(chunk_texts)

    return {
        "content": text,
        "prompt_name": prompt["name"],
        "prompt_version": prompt["version"],
    }


def _deterministic_summary(chunk_texts: list[str]) -> str:
    if not chunk_texts:
        return "No content available to summarize."
    preview = "\n".join(f"- {text[:140].strip()}" for text in chunk_texts[:5])
    return "# Summary\n\n## Key Points\n" + preview
