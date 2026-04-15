from __future__ import annotations

from packages.core.config.loader import get_settings
from packages.llm.base import LLMProvider, LLMRequest, LLMResponse
from packages.llm.ollama_provider import OllamaProvider


class EchoProvider:
    def __init__(self, model: str = "echo-local"):
        self.model = model

    def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(text=request.prompt[:512], model=self.model)


def get_default_llm_provider() -> LLMProvider:
    settings = get_settings()
    llm_cfg = settings.model_provider.get("llm", {})

    provider = str(llm_cfg.get("provider", "echo")).lower()
    model = str(llm_cfg.get("model", "echo-local"))
    timeout_seconds = int(llm_cfg.get("timeout_seconds", 60))
    base_url = str(llm_cfg.get("base_url", "http://127.0.0.1:11434"))

    if provider == "ollama":
        return OllamaProvider(model=model, base_url=base_url, timeout_seconds=timeout_seconds)

    return EchoProvider(model=model)
