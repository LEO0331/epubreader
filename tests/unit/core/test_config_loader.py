from __future__ import annotations

from pathlib import Path

from packages.core.config.loader import load_settings


def test_load_settings_with_env_override(monkeypatch):
    monkeypatch.setenv("APP_NAME", "override-name")
    monkeypatch.setenv("APP_PORT", "9010")

    settings = load_settings(config_dir=str(Path("configs").resolve()))

    assert settings.app.name == "override-name"
    assert settings.app.port == 9010
    assert settings.models.profile in {"local", "api"}
