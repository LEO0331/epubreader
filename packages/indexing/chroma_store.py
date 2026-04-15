from __future__ import annotations

from pathlib import Path
from typing import Any, TypedDict, cast

import chromadb
from chromadb.api.models.Collection import Collection


class VectorRecord(TypedDict):
    id: str
    document: str
    embedding: list[float]
    metadata: dict[str, str]


def collection_name_for_book(book_id: str) -> str:
    safe = "".join(ch for ch in book_id.lower() if ch.isalnum() or ch in {"_", "-"})
    safe = safe.replace("-", "_")
    return f"book_{safe}"


class ChromaStore:
    def __init__(self, persist_path: str):
        path = Path(persist_path)
        path.mkdir(parents=True, exist_ok=True)
        self.persist_path = path
        self.client = chromadb.PersistentClient(path=str(path))

    def get_or_create_collection(
        self,
        *,
        name: str,
        metadata: dict[str, str] | None = None,
    ) -> Collection:
        if metadata:
            return self.client.get_or_create_collection(name=name, metadata=metadata)
        return self.client.get_or_create_collection(name=name)

    def upsert(self, *, collection_name: str, records: list[VectorRecord]) -> None:
        collection = self.get_or_create_collection(name=collection_name)
        collection_any = cast(Any, collection)
        collection_any.upsert(
            ids=[r["id"] for r in records],
            documents=[r["document"] for r in records],
            embeddings=[r["embedding"] for r in records],
            metadatas=[r["metadata"] for r in records],
        )

    def query(
        self,
        *,
        collection_name: str,
        query_embedding: list[float],
        n_results: int = 5,
    ) -> list[dict[str, object]]:
        collection = self.get_or_create_collection(name=collection_name)
        collection_any = cast(Any, collection)
        raw = collection_any.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )

        ids_raw = raw.get("ids")
        ids = ids_raw[0] if ids_raw else []
        documents_raw = raw.get("documents")
        documents = documents_raw[0] if documents_raw else []
        metadatas_raw = raw.get("metadatas")
        metadatas = metadatas_raw[0] if metadatas_raw else []
        distances_raw = raw.get("distances")
        distances = distances_raw[0] if distances_raw else []

        results: list[dict[str, object]] = []
        for idx, rec_id in enumerate(ids):
            metadata_value: Any = metadatas[idx] if idx < len(metadatas) else None
            results.append(
                {
                    "id": rec_id,
                    "document": documents[idx] if idx < len(documents) else None,
                    "metadata": metadata_value,
                    "distance": distances[idx] if idx < len(distances) else None,
                }
            )
        return results

    def delete_collection(self, *, name: str) -> None:
        self.client.delete_collection(name=name)

    def list_collections(self) -> list[str]:
        collections = self.client.list_collections()
        names: list[str] = []
        for item in collections:
            if isinstance(item, str):
                names.append(item)
            else:
                names.append(item.name)
        return names
