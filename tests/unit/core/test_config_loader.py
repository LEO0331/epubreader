from __future__ import annotations

from pathlib import Path

import pytest

from packages.core.config.loader import load_settings


def test_load_settings_with_env_override(monkeypatch):
    monkeypatch.setenv("APP_NAME", "override-name")
    monkeypatch.setenv("APP_PORT", "9010")
    monkeypatch.setenv("APP_OCR_LANGS", "chi_tra+eng")
    monkeypatch.setenv("APP_OCR_MIN_TEXT_CHARS", "120")
    monkeypatch.setenv("APP_OCR_MAX_PAGES", "25")
    monkeypatch.setenv("APP_OCR_PAGE_TIMEOUT_SECONDS", "7")
    monkeypatch.setenv("APP_OCR_TOTAL_TIMEOUT_SECONDS", "45")
    monkeypatch.setenv("APP_OCR_ISOLATE_WORKER", "true")
    monkeypatch.setenv("APP_INGEST_HOST_ALLOWLIST_ENABLED", "true")
    monkeypatch.setenv("APP_INGEST_HOST_ALLOWLIST", "example.com,cdn.example.com")

    settings = load_settings(config_dir=str(Path("configs").resolve()))

    assert settings.app.name == "override-name"
    assert settings.app.port == 9010
    assert settings.app.ocr_langs == "chi_tra+eng"
    assert settings.app.ocr_min_text_chars == 120
    assert settings.app.ocr_max_pages == 25
    assert settings.app.ocr_page_timeout_seconds == 7
    assert settings.app.ocr_total_timeout_seconds == 45
    assert settings.app.ocr_isolate_worker is True
    assert settings.app.ingest_host_allowlist_enabled is True
    assert settings.app.ingest_host_allowlist == ["example.com", "cdn.example.com"]
    assert settings.models.profile in {"local", "api"}


def test_load_settings_requires_api_key_for_non_local(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("APP_API_KEY", raising=False)

    with pytest.raises(ValueError):
        load_settings(config_dir=str(Path("configs").resolve()))
