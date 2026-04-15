from __future__ import annotations

from packages.llm.base import LLMProvider, LLMProviderError, LLMRequest
from packages.prompts.loader import PromptLoader


def generate_skill(
    *,
    provider: LLMProvider,
    prompt_loader: PromptLoader,
    summary_text: str,
    force: bool = False,
) -> dict[str, str] | None:
    genre = classify_genre(
        provider=provider,
        prompt_loader=prompt_loader,
        content=summary_text,
    )
    eligible = force or any(
        key in genre.lower() for key in ["non-fiction", "technical", "tutorial"]
    )
    if not eligible:
        return None

    prompt = prompt_loader.load("skill_extract", variables={"content": summary_text})
    try:
        response = provider.generate(
            LLMRequest(prompt=prompt["content"], temperature=0.0, max_tokens=800)
        )
        text = response.text.strip()
    except LLMProviderError:
        text = (
            f"# Skills\n\n- Derived from genre: {genre}\n"
            "- Extracted actionable steps from summary"
        )

    return {
        "content": text,
        "genre": genre,
        "prompt_name": prompt["name"],
        "prompt_version": prompt["version"],
    }


def classify_genre(*, provider: LLMProvider, prompt_loader: PromptLoader, content: str) -> str:
    prompt = prompt_loader.load("classify_genre", variables={"content": content[:2000]})
    try:
        response = provider.generate(
            LLMRequest(prompt=prompt["content"], temperature=0.0, max_tokens=40)
        )
        label = response.text.strip().splitlines()[0][:80]
        return label or "unknown"
    except LLMProviderError:
        return "non-fiction"
