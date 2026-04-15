from __future__ import annotations

from bs4 import BeautifulSoup

_REMOVAL_TAGS = {"nav", "header", "footer", "script", "style", "noscript", "aside"}


def parse_html(raw_html: bytes) -> dict[str, object]:
    soup = BeautifulSoup(raw_html, "lxml")

    for tag in soup.find_all(_REMOVAL_TAGS):
        tag.decompose()

    for cls in soup.find_all(attrs={"class": True}):
        class_attr = cls.get("class")
        if isinstance(class_attr, list):
            classes = " ".join(str(part) for part in class_attr)
        elif isinstance(class_attr, str):
            classes = class_attr
        else:
            classes = ""
        if any(noise in classes.lower() for noise in ["nav", "menu", "breadcrumb", "footer"]):
            cls.decompose()

    title = _text_or_none(soup.title.get_text(" ", strip=True)) if soup.title else None

    sections: list[dict[str, object]] = []
    heading_stack: list[str] = []
    ordinal = 0

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
                "source_locator": "html",
            }
        )
        ordinal += 1

    return {
        "metadata": {
            "title": title,
            "author": None,
            "language": None,
            "toc": [],
        },
        "sections": sections,
    }


def _text_or_none(value: str) -> str | None:
    text = value.strip()
    return text if text else None
