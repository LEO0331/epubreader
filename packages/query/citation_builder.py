from __future__ import annotations


def build_citations(retrieved: list[dict[str, object]]) -> list[dict[str, object]]:
    citations: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()

    for row in retrieved:
        metadata = row.get("metadata")
        md = metadata if isinstance(metadata, dict) else {}

        book_id = str(md.get("book_id", ""))
        chunk_id = str(md.get("chunk_id", row.get("id", "")))
        section_id = str(md.get("section_id", ""))

        key = (book_id, chunk_id)
        if key in seen:
            continue
        seen.add(key)

        citations.append(
            {
                "book_id": book_id,
                "section_id": section_id,
                "chunk_id": chunk_id,
                "distance": row.get("distance"),
                "snippet": str(row.get("document", ""))[:220],
            }
        )

    return citations
