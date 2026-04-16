from __future__ import annotations

from pathlib import Path

from packages.parsing.pdf_parser import parse_pdf


class _FakePage:
    def __init__(self, text: str):
        self._text = text

    def extract_text(self) -> str:
        return self._text


class _FakeReader:
    def __init__(self, pages: list[_FakePage], metadata: dict[str, str] | None = None):
        self.pages = pages
        self.metadata = metadata or {}


def test_parse_pdf_text_first_path(monkeypatch, tmp_path: Path):
    reader = _FakeReader(
        pages=[_FakePage("This is embedded text."), _FakePage("")],
        metadata={"/Title": "PDF Title", "/Author": "PDF Author"},
    )

    monkeypatch.setattr("packages.parsing.pdf_parser._load_pdf_reader", lambda _: reader)

    out = parse_pdf(tmp_path / "demo.pdf", ocr_enabled=False)

    assert out["metadata"]["title"] == "PDF Title"
    assert out["metadata"]["author"] == "PDF Author"
    assert out["metadata"]["ocr"]["enabled"] is False
    assert len(out["sections"]) == 1
    assert out["sections"][0]["source_locator"] == "page:1"


def test_parse_pdf_ocr_fallback_used(monkeypatch, tmp_path: Path):
    reader = _FakeReader(pages=[_FakePage("a")])
    monkeypatch.setattr("packages.parsing.pdf_parser._load_pdf_reader", lambda _: reader)
    monkeypatch.setattr(
        "packages.parsing.pdf_parser._ocr_extract_page_text",
        lambda **_: ("OCR Mandarin English text", True),
    )

    out = parse_pdf(tmp_path / "demo.pdf", ocr_enabled=True, ocr_min_text_chars=5)

    assert out["metadata"]["ocr"]["attempted_pages"] == 1
    assert out["metadata"]["ocr"]["used_pages"] == 1
    assert out["metadata"]["ocr"]["available"] is True
    assert out["sections"][0]["content"] == "OCR Mandarin English text"


def test_parse_pdf_graceful_when_ocr_unavailable(monkeypatch, tmp_path: Path):
    reader = _FakeReader(pages=[_FakePage("")])
    monkeypatch.setattr("packages.parsing.pdf_parser._load_pdf_reader", lambda _: reader)
    monkeypatch.setattr(
        "packages.parsing.pdf_parser._ocr_extract_page_text",
        lambda **_: ("", False),
    )

    out = parse_pdf(tmp_path / "demo.pdf", ocr_enabled=True, ocr_min_text_chars=1)

    assert out["metadata"]["ocr"]["attempted_pages"] == 1
    assert out["metadata"]["ocr"]["used_pages"] == 0
    assert out["metadata"]["ocr"]["available"] is False
    assert out["sections"] == []


def test_parse_pdf_respects_ocr_max_pages(monkeypatch, tmp_path: Path):
    reader = _FakeReader(pages=[_FakePage(""), _FakePage("")])
    monkeypatch.setattr("packages.parsing.pdf_parser._load_pdf_reader", lambda _: reader)

    calls = {"count": 0}

    def _fake_ocr_extract(**_kwargs):
        calls["count"] += 1
        return ("Recovered text", True)

    monkeypatch.setattr("packages.parsing.pdf_parser._ocr_extract_page_text", _fake_ocr_extract)

    out = parse_pdf(
        tmp_path / "demo.pdf",
        ocr_enabled=True,
        ocr_min_text_chars=1,
        ocr_max_pages=1,
    )

    assert calls["count"] == 1
    assert out["metadata"]["ocr"]["attempted_pages"] == 1
    assert out["metadata"]["ocr"]["skipped_due_to_limits"] == 1
    assert len(out["sections"]) == 1


def test_parse_pdf_routes_to_isolated_ocr_when_enabled(monkeypatch, tmp_path: Path):
    reader = _FakeReader(pages=[_FakePage("")])
    monkeypatch.setattr("packages.parsing.pdf_parser._load_pdf_reader", lambda _: reader)

    captured = {"isolate_worker": False, "page_timeout_seconds": 0}

    def _fake_ocr_extract(**kwargs):
        captured["isolate_worker"] = bool(kwargs.get("isolate_worker"))
        captured["page_timeout_seconds"] = int(kwargs.get("page_timeout_seconds", 0))
        return ("Isolated OCR text", True)

    monkeypatch.setattr("packages.parsing.pdf_parser._ocr_extract_page_text", _fake_ocr_extract)

    out = parse_pdf(
        tmp_path / "demo.pdf",
        ocr_enabled=True,
        ocr_min_text_chars=1,
        ocr_isolate_worker=True,
        ocr_page_timeout_seconds=4,
    )

    assert captured["isolate_worker"] is True
    assert captured["page_timeout_seconds"] == 4
    assert out["sections"][0]["content"] == "Isolated OCR text"
