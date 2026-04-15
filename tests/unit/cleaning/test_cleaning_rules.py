from __future__ import annotations

from packages.cleaning.rules import is_boilerplate, normalize_text, repair_heading


def test_normalize_text_and_boilerplate_filter():
    assert normalize_text("  A\n\tB  ") == "A B"
    assert is_boilerplate("Page 3")
    assert not is_boilerplate("Actual chapter content")


def test_repair_heading_fallback():
    content = "Heading like line with several words and additional text"
    repaired = repair_heading(None, content)
    assert repaired is not None
    assert repaired.startswith("Heading like line")
