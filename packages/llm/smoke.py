from __future__ import annotations

from packages.llm.base import LLMRequest, LLMResponse
from packages.llm.router import get_default_llm_provider


def run_provider_smoke_test(prompt: str = "Respond with: OK") -> LLMResponse:
    provider = get_default_llm_provider()
    return provider.generate(LLMRequest(prompt=prompt, temperature=0.0, max_tokens=32))
