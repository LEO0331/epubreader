from __future__ import annotations

from uuid import uuid4

from sqlalchemy.orm import Session

from packages.embeddings import EmbeddingRequest, get_default_embedding_provider
from packages.llm import LLMProviderError, LLMRequest, get_default_llm_provider
from packages.prompts import PromptLoader
from packages.query.citation_builder import build_citations
from packages.query.index_builder import IndexBuilder
from packages.storage.repositories.books_repo import BooksRepository
from packages.storage.repositories.collections_repo import CollectionsRepository
from packages.storage.repositories.queries_repo import QueriesRepository


class QueryEngine:
    def __init__(self, session: Session, data_root: str, prompts_dir: str):
        self.session = session
        self.books = BooksRepository(session)
        self.collections = CollectionsRepository(session)
        self.queries = QueriesRepository(session)
        self.index_builder = IndexBuilder(session=session, data_root=data_root)
        self.embedder = get_default_embedding_provider()
        self.llm = get_default_llm_provider()
        self.prompts = PromptLoader(prompts_dir)

    def preview(
        self,
        *,
        question: str,
        book_ids: list[str] | None,
        collection_id: str | None,
        top_k: int,
    ) -> dict[str, object]:
        target_book_ids = self._resolve_book_scope(book_ids=book_ids, collection_id=collection_id)
        index_stats = self.index_builder.build_for_books(book_ids=target_book_ids)

        qvec = self.embedder.embed(EmbeddingRequest(texts=[question])).vectors[0]

        retrieved: list[dict[str, object]] = []
        for item in index_stats:
            rows = self.index_builder.store.query(
                collection_name=item.collection_name,
                query_embedding=qvec,
                n_results=top_k,
            )
            retrieved.extend(rows)

        retrieved.sort(key=lambda x: _distance(x.get("distance")))
        top = retrieved[:top_k]

        return {
            "question": question,
            "book_ids": target_book_ids,
            "evidence": top,
            "diagnostics": {
                "indexed_books": len(index_stats),
                "retrieved_count": len(top),
                "index_stats": [
                    {
                        "book_id": s.book_id,
                        "collection_name": s.collection_name,
                        "chunk_count": s.chunk_count,
                    }
                    for s in index_stats
                ],
            },
        }

    def answer(
        self,
        *,
        question: str,
        book_ids: list[str] | None,
        collection_id: str | None,
        top_k: int,
    ) -> dict[str, object]:
        preview = self.preview(
            question=question,
            book_ids=book_ids,
            collection_id=collection_id,
            top_k=top_k,
        )
        evidence = preview["evidence"]
        evidence_rows = evidence if isinstance(evidence, list) else []

        if not evidence_rows:
            raise ValueError("No retrieved evidence found; cannot answer without citations.")

        evidence_text = "\n".join(
            f"[{row.get('id')}] {str(row.get('document', ''))[:400]}"
            for row in evidence_rows
        )
        prompt = self.prompts.load(
            "answer_with_citations",
            variables={
                "question": question,
                "evidence": evidence_text,
            },
        )

        try:
            response = self.llm.generate(
                LLMRequest(prompt=prompt["content"], temperature=0.0, max_tokens=700)
            )
            answer_text = response.text.strip()
        except LLMProviderError:
            answer_text = self._fallback_answer(evidence_rows)

        citations = build_citations(evidence_rows)

        self.queries.create(
            query_id=str(uuid4()),
            question=question,
            book_scope=preview["book_ids"] if isinstance(preview["book_ids"], list) else [],
            response_preview=answer_text[:280],
        )
        self.session.commit()

        return {
            "question": question,
            "answer": answer_text,
            "citations": citations,
            "retrieval_diagnostics": preview["diagnostics"],
        }

    def _resolve_book_scope(
        self,
        *,
        book_ids: list[str] | None,
        collection_id: str | None,
    ) -> list[str]:
        if book_ids:
            return book_ids
        if collection_id:
            return self.collections.list_books(collection_id)
        rows = self.books.list(limit=100000, offset=0)
        return [row.id for row in rows]

    def _fallback_answer(self, evidence_rows: list[dict[str, object]]) -> str:
        lines = ["Answer synthesized from retrieved evidence:"]
        for row in evidence_rows[:3]:
            lines.append(f"- [{row.get('id')}] {str(row.get('document', ''))[:220]}")
        return "\n".join(lines)


def _distance(value: object) -> float:
    if isinstance(value, (int, float, str)):
        try:
            return float(value)
        except ValueError:
            return 1e9
    try:
        return float(str(value)) if value is not None else 1e9
    except (TypeError, ValueError):
        return 1e9
