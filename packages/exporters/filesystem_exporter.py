from __future__ import annotations

import json
from pathlib import Path


def export_filesystem(
    *,
    output_dir: Path,
    collection_name: str,
    books: list[dict[str, object]],
) -> Path:
    target = output_dir / "filesystem" / _slug(collection_name)
    target.mkdir(parents=True, exist_ok=True)

    for book in sorted(books, key=lambda b: str(b.get("id", ""))):
        book_id = str(book["id"])
        book_dir = target / book_id
        book_dir.mkdir(parents=True, exist_ok=True)

        (book_dir / "summary.md").write_text(str(book.get("summary", "")), encoding="utf-8")
        (book_dir / "wiki.md").write_text(str(book.get("wiki", "")), encoding="utf-8")
        (book_dir / "qa.jsonl").write_text(str(book.get("qa", "")), encoding="utf-8")

    manifest = {
        "collection": collection_name,
        "book_count": len(books),
        "books": [str(b.get("id", "")) for b in books],
    }
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return target


def _slug(value: str) -> str:
    clean = "".join(ch.lower() if ch.isalnum() else "_" for ch in value)
    while "__" in clean:
        clean = clean.replace("__", "_")
    return clean.strip("_") or "collection"
