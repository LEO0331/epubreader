from __future__ import annotations

from packages.core.config.loader import get_settings
from packages.embeddings.base import EmbeddingProvider
from packages.embeddings.local_provider import LocalEmbeddingProvider


def get_default_embedding_provider() -> EmbeddingProvider:
    settings = get_settings()
    cfg = settings.model_provider.get("embeddings", {})
    provider = str(cfg.get("provider", "local-placeholder")).lower()
    model = str(cfg.get("model", "local-hash-v1"))

    if provider in {"local", "local-placeholder", "api-placeholder", "api"}:
        return LocalEmbeddingProvider(model=model)

    return LocalEmbeddingProvider(model=model)
