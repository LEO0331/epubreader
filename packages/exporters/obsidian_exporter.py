from __future__ import annotations

from pathlib import Path


def export_obsidian(
    *,
    output_dir: Path,
    collection_name: str,
    books: list[dict[str, object]],
) -> Path:
    target = output_dir / "obsidian" / _slug(collection_name)
    target.mkdir(parents=True, exist_ok=True)

    index_lines = [f"# {collection_name}", ""]
    for book in sorted(books, key=lambda b: str(b.get("id", ""))):
        book_id = str(book["id"])
        note_name = f"{book_id}.md"
        index_lines.append(f"- [[{book_id}]]")

        note = [
            f"# {book_id}",
            "",
            "## Summary",
            str(book.get("summary", "")),
            "",
            "## Wiki",
            str(book.get("wiki", "")),
        ]
        (target / note_name).write_text("\n".join(note), encoding="utf-8")

    (target / "index.md").write_text("\n".join(index_lines), encoding="utf-8")
    return target


def _slug(value: str) -> str:
    clean = "".join(ch.lower() if ch.isalnum() else "_" for ch in value)
    while "__" in clean:
        clean = clean.replace("__", "_")
    return clean.strip("_") or "collection"
