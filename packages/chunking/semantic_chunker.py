from __future__ import annotations

import re

from packages.chunking.structure_chunker import ChunkOutput, _stable_chunk_id

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


class SemanticChunker:
    def __init__(self, *, max_words: int = 260, target_words: int = 180):
        self.max_words = max_words
        self.target_words = target_words

    def split_oversized_chunk(
        self,
        *,
        book_id: str,
        section_id: str,
        section_ordinal: int,
        text: str,
        base_metadata: dict[str, str],
    ) -> list[ChunkOutput]:
        sentences = [s.strip() for s in _SENTENCE_SPLIT_RE.split(text) if s.strip()]
        if not sentences:
            sentences = [text]

        text_chunks: list[str] = []
        current_parts: list[str] = []
        current_words = 0

        for sentence in sentences:
            sentence_words = len(sentence.split())
            if current_parts and current_words + sentence_words > self.target_words:
                text_chunks.append(" ".join(current_parts).strip())
                current_parts = [sentence]
                current_words = sentence_words
            else:
                current_parts.append(sentence)
                current_words += sentence_words

        if current_parts:
            text_chunks.append(" ".join(current_parts).strip())

        out: list[ChunkOutput] = []
        for local_idx, chunk_text in enumerate(text_chunks):
            metadata = dict(base_metadata)
            metadata["chunker"] = "semantic_fallback"
            out.append(
                {
                    "id": _stable_chunk_id(
                        book_id=book_id,
                        section_id=section_id,
                        section_ordinal=section_ordinal,
                        local_index=local_idx,
                        text=chunk_text,
                    ),
                    "section_id": section_id,
                    "ordinal": local_idx,
                    "text": chunk_text,
                    "metadata": metadata,
                }
            )

        return out
