from __future__ import annotations

import hashlib

from packages.embeddings.base import EmbeddingRequest, EmbeddingResponse


class LocalEmbeddingProvider:
    def __init__(self, model: str = "local-hash-v1", dimensions: int = 64):
        self.model = model
        self.dimensions = dimensions

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        vectors = [self._embed_one(text) for text in request.texts]
        return EmbeddingResponse(vectors=vectors, model=self.model)

    def _embed_one(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        seed = list(digest)

        values: list[float] = []
        for i in range(self.dimensions):
            b = seed[i % len(seed)]
            values.append((float(b) / 255.0) * 2.0 - 1.0)

        norm = sum(x * x for x in values) ** 0.5
        if norm == 0:
            return values
        return [x / norm for x in values]
