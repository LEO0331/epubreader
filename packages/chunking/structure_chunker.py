from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import TypedDict

_WORD_RE = re.compile(r"\S+")


class SectionInput(TypedDict):
    id: str
    ordinal: int
    heading: str | None
    heading_path: list[str]
    content: str


class ChunkOutput(TypedDict):
    id: str
    section_id: str
    ordinal: int
    text: str
    metadata: dict[str, str]


@dataclass(frozen=True)
class ChunkPolicy:
    target_words: int = 180
    max_words: int = 260


class StructureChunker:
    def __init__(self, policy: ChunkPolicy | None = None):
        self.policy = policy or ChunkPolicy()

    def chunk_sections(
        self,
        *,
        book_id: str,
        language: str | None,
        sections: list[SectionInput],
    ) -> list[ChunkOutput]:
        chunks: list[ChunkOutput] = []
        for section in sections:
            chunks.extend(
                self._chunk_one_section(
                    book_id=book_id,
                    language=language,
                    section=section,
                )
            )

        for idx, chunk in enumerate(chunks):
            chunk["ordinal"] = idx
        return chunks

    def _chunk_one_section(
        self,
        *,
        book_id: str,
        language: str | None,
        section: SectionInput,
    ) -> list[ChunkOutput]:
        section_id = section["id"]
        section_ordinal = section["ordinal"]
        heading = section["heading"]
        heading_path_list = section["heading_path"]
        chapter = heading_path_list[0] if heading_path_list else heading

        text = section["content"].strip()
        if not text:
            return []

        paragraphs = [part.strip() for part in text.split("\n") if part.strip()]
        if not paragraphs:
            paragraphs = [text]

        grouped: list[str] = []
        current_parts: list[str] = []
        current_words = 0
        for para in paragraphs:
            para_words = len(_WORD_RE.findall(para))
            would_exceed = (
                current_words > 0
                and (current_words + para_words) > self.policy.target_words
            )
            if would_exceed:
                grouped.append("\n\n".join(current_parts).strip())
                current_parts = [para]
                current_words = para_words
            else:
                current_parts.append(para)
                current_words += para_words

        if current_parts:
            grouped.append("\n\n".join(current_parts).strip())

        chunks: list[ChunkOutput] = []
        for local_idx, grouped_text in enumerate(grouped):
            chunk_id = _stable_chunk_id(
                book_id=book_id,
                section_id=section_id,
                section_ordinal=section_ordinal,
                local_index=local_idx,
                text=grouped_text,
            )
            metadata = {
                "book_id": book_id,
                "section_id": section_id,
                "section_ordinal": str(section_ordinal),
                "chapter": chapter or "",
                "heading": heading or "",
                "heading_path": " > ".join(heading_path_list),
                "language": language or "",
                "chunker": "structure",
            }
            chunks.append(
                {
                    "id": chunk_id,
                    "section_id": section_id,
                    "ordinal": local_idx,
                    "text": grouped_text,
                    "metadata": metadata,
                }
            )

        return chunks


def word_count(text: str) -> int:
    return len(_WORD_RE.findall(text))


def _stable_chunk_id(
    *,
    book_id: str,
    section_id: str,
    section_ordinal: int,
    local_index: int,
    text: str,
) -> str:
    digest = hashlib.sha1(
        f"{book_id}|{section_id}|{section_ordinal}|{local_index}|{text}".encode()
    ).hexdigest()
    return f"chk_{digest[:24]}"
