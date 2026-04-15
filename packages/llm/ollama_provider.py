from __future__ import annotations

import httpx

from packages.llm.base import LLMProviderError, LLMRequest, LLMResponse


class OllamaProvider:
    def __init__(
        self,
        *,
        model: str,
        base_url: str = "http://127.0.0.1:11434",
        timeout_seconds: int = 60,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def generate(self, request: LLMRequest) -> LLMResponse:
        prompt = request.prompt
        if request.system is not None:
            prompt = f"{request.system}\n\n{request.prompt}"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": request.temperature,
            },
        }
        try:
            response = httpx.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            body = response.json()
        except httpx.TimeoutException as exc:
            raise LLMProviderError("timeout", "Ollama request timed out") from exc
        except httpx.HTTPStatusError as exc:
            raise LLMProviderError(
                "http_error",
                f"Ollama HTTP error: {exc.response.status_code}",
            ) from exc
        except httpx.HTTPError as exc:
            raise LLMProviderError("network_error", "Failed to reach Ollama service") from exc
        except ValueError as exc:
            raise LLMProviderError("decode_error", "Ollama returned invalid JSON") from exc

        text = body.get("response")
        if not isinstance(text, str):
            raise LLMProviderError("invalid_payload", "Ollama response missing text")

        return LLMResponse(
            text=text.strip(),
            model=str(body.get("model", self.model)),
            usage_prompt_tokens=(
                int(body["prompt_eval_count"])
                if isinstance(body.get("prompt_eval_count"), int)
                else None
            ),
            usage_completion_tokens=(
                int(body["eval_count"]) if isinstance(body.get("eval_count"), int) else None
            ),
        )
