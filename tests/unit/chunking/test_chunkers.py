from __future__ import annotations

from packages.chunking.semantic_chunker import SemanticChunker
from packages.chunking.structure_chunker import StructureChunker


def test_structure_chunker_is_deterministic_for_same_input():
    chunker = StructureChunker()
    sections = [
        {
            "id": "sec-1",
            "ordinal": 0,
            "heading": "Intro",
            "heading_path": ["Intro"],
            "content": "Paragraph one.\n\nParagraph two.",
        }
    ]

    a = chunker.chunk_sections(book_id="book-1", language="en", sections=sections)
    b = chunker.chunk_sections(book_id="book-1", language="en", sections=sections)

    assert [x["id"] for x in a] == [x["id"] for x in b]
    assert a[0]["metadata"]["heading"] == "Intro"


def test_semantic_chunker_splits_large_text():
    chunker = SemanticChunker(max_words=20, target_words=8)
    text = "One two three four five six seven eight. Nine ten eleven twelve thirteen fourteen."

    chunks = chunker.split_oversized_chunk(
        book_id="book-1",
        section_id="sec-1",
        section_ordinal=0,
        text=text,
        base_metadata={"book_id": "book-1", "section_ordinal": "0"},
    )

    assert len(chunks) >= 2
    assert all(c["metadata"]["chunker"] == "semantic_fallback" for c in chunks)
