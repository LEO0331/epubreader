from __future__ import annotations

from packages.core.config.loader import get_settings
from packages.llm.base import LLMRequest
from packages.llm.router import EchoProvider


def test_echo_provider_returns_prompt_prefix():
    provider = EchoProvider(model="echo")
    response = provider.generate(LLMRequest(prompt="hello world"))

    assert response.model == "echo"
    assert "hello world" in response.text


def test_settings_model_provider_mapping_available():
    settings = get_settings()
    assert isinstance(settings.model_provider, dict)
