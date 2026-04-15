from __future__ import annotations

from packages.llm.base import LLMProvider, LLMProviderError, LLMRequest
from packages.prompts.loader import PromptLoader


def generate_wiki(
    *,
    provider: LLMProvider,
    prompt_loader: PromptLoader,
    summary_text: str,
) -> dict[str, str]:
    prompt = prompt_loader.load("wiki_transform", variables={"content": summary_text})
    try:
        response = provider.generate(
            LLMRequest(prompt=prompt["content"], temperature=0.0, max_tokens=900)
        )
        text = response.text.strip()
    except LLMProviderError:
        text = f"# Wiki\n\n## Overview\n{summary_text[:1000]}"

    return {
        "content": text,
        "prompt_name": prompt["name"],
        "prompt_version": prompt["version"],
    }
