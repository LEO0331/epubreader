from __future__ import annotations

from pathlib import Path

from packages.embeddings.base import EmbeddingRequest
from packages.embeddings.local_provider import LocalEmbeddingProvider
from packages.indexing.chroma_store import ChromaStore, collection_name_for_book


def test_chroma_store_persists_vectors_across_restart(tmp_path: Path):
    provider = LocalEmbeddingProvider(dimensions=32)

    store1 = ChromaStore(persist_path=str(tmp_path / "chroma"))
    name = collection_name_for_book("Book-123")

    docs = ["alpha text", "beta text", "gamma text"]
    vectors = provider.embed(EmbeddingRequest(texts=docs)).vectors
    store1.get_or_create_collection(name=name, metadata={"book_id": "Book-123", "scope": "book"})
    store1.upsert(
        collection_name=name,
        records=[
            {
                "id": f"c-{idx}",
                "document": docs[idx],
                "embedding": vectors[idx],
                "metadata": {"chunk_id": f"c-{idx}", "book_id": "Book-123"},
            }
            for idx in range(len(docs))
        ],
    )

    store2 = ChromaStore(persist_path=str(tmp_path / "chroma"))
    query_vec = provider.embed(EmbeddingRequest(texts=["alpha text"])).vectors[0]
    results = store2.query(collection_name=name, query_embedding=query_vec, n_results=2)

    assert len(results) >= 1
    assert results[0]["metadata"] is not None
    assert results[0]["id"] in {"c-0", "c-1", "c-2"}


def test_collection_metadata_is_preserved(tmp_path: Path):
    store = ChromaStore(persist_path=str(tmp_path / "chroma"))
    name = collection_name_for_book("Book-XYZ")

    collection = store.get_or_create_collection(
        name=name,
        metadata={"book_id": "Book-XYZ", "scope": "book", "strategy": "book_id_v1"},
    )

    assert collection.metadata is not None
    assert collection.metadata.get("book_id") == "Book-XYZ"
    assert collection.metadata.get("strategy") == "book_id_v1"
