from __future__ import annotations

from pathlib import Path

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub


def parse_epub(path: Path) -> dict[str, object]:
    book = epub.read_epub(str(path))

    title = _first_or_none(book.get_metadata("DC", "title"))
    author = _first_or_none(book.get_metadata("DC", "creator"))
    language = _first_or_none(book.get_metadata("DC", "language"))

    toc_entries = _flatten_toc(book.toc)

    sections: list[dict[str, object]] = []
    heading_stack: list[str] = []
    ordinal = 0

    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        html = item.get_content().decode("utf-8", errors="ignore")
        soup = BeautifulSoup(html, "lxml")

        for node in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p"]):
            text = node.get_text(" ", strip=True)
            if not text:
                continue

            if node.name and node.name.startswith("h"):
                level = int(node.name[1])
                heading_stack = heading_stack[: max(level - 1, 0)]
                heading_stack.append(text)
                continue

            heading = heading_stack[-1] if heading_stack else None
            sections.append(
                {
                    "ordinal": ordinal,
                    "heading": heading,
                    "heading_path": heading_stack.copy(),
                    "content": text,
                    "source_locator": item.get_name(),
                }
            )
            ordinal += 1

    return {
        "metadata": {
            "title": title,
            "author": author,
            "language": language,
            "toc": toc_entries,
        },
        "sections": sections,
    }


def _flatten_toc(toc: tuple[object, ...] | list[object]) -> list[str]:
    flattened: list[str] = []
    for item in toc:
        label = _toc_label(item)
        if label:
            flattened.append(label)

        if isinstance(item, (list, tuple)):
            flattened.extend(_flatten_toc(item))
        else:
            children = getattr(item, "subitems", None)
            if isinstance(children, (list, tuple)):
                flattened.extend(_flatten_toc(children))
    return flattened


def _toc_label(item: object) -> str | None:
    title = getattr(item, "title", None)
    if isinstance(title, str) and title.strip():
        return title.strip()

    if isinstance(item, tuple) and len(item) > 0:
        first = item[0]
        if isinstance(first, str) and first.strip():
            return first.strip()
        first_title = getattr(first, "title", None)
        if isinstance(first_title, str) and first_title.strip():
            return first_title.strip()

    return None


def _first_or_none(metadata: list[tuple[str, dict[str, str]]]) -> str | None:
    if not metadata:
        return None
    value = metadata[0][0]
    return value if value else None
