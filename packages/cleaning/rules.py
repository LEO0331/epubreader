from __future__ import annotations

import re
import unicodedata

_WS_RE = re.compile(r"\s+")

_BOILERPLATE_PATTERNS = [
    re.compile(r"^page\s+\d+$", re.IGNORECASE),
    re.compile(r"^copyright\b", re.IGNORECASE),
    re.compile(r"^all rights reserved\b", re.IGNORECASE),
]


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    normalized = _WS_RE.sub(" ", normalized).strip()
    return normalized


def is_boilerplate(text: str) -> bool:
    plain = normalize_text(text)
    if not plain:
        return True
    return any(pattern.match(plain) for pattern in _BOILERPLATE_PATTERNS)


def repair_heading(heading: str | None, content: str) -> str | None:
    if heading:
        cleaned = normalize_text(heading)
        return cleaned if cleaned else None

    prefix = normalize_text(content)[:80]
    if not prefix:
        return None
    words = prefix.split(" ")
    if len(words) <= 10:
        return prefix
    return " ".join(words[:10])
