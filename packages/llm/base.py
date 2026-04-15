from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LLMRequest:
    prompt: str
    system: str | None = None
    temperature: float = 0.0
    max_tokens: int = 512


@dataclass(frozen=True)
class LLMResponse:
    text: str
    model: str
    usage_prompt_tokens: int | None = None
    usage_completion_tokens: int | None = None


class LLMProviderError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class LLMProvider(Protocol):
    def generate(self, request: LLMRequest) -> LLMResponse:
        ...
