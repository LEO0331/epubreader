from __future__ import annotations

from pathlib import Path


def export_github(
    *,
    output_dir: Path,
    collection_name: str,
    books: list[dict[str, object]],
) -> Path:
    target = output_dir / "github" / _slug(collection_name)
    target.mkdir(parents=True, exist_ok=True)

    lines = [f"# {collection_name}", "", "Generated export package.", ""]
    for book in sorted(books, key=lambda b: str(b.get("id", ""))):
        book_id = str(book["id"])
        lines.append(f"## {book_id}")
        lines.append("")
        lines.append("### Summary")
        lines.append(str(book.get("summary", "")))
        lines.append("")
        lines.append("### Wiki")
        lines.append(str(book.get("wiki", "")))
        lines.append("")

    (target / "README.md").write_text("\n".join(lines), encoding="utf-8")
    return target


def _slug(value: str) -> str:
    clean = "".join(ch.lower() if ch.isalnum() else "_" for ch in value)
    while "__" in clean:
        clean = clean.replace("__", "_")
    return clean.strip("_") or "collection"
