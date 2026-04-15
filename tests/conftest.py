from __future__ import annotations

from pathlib import Path

import pytest

from packages.core.config.loader import reset_settings_cache
from packages.storage.db.session import reset_db_state


@pytest.fixture(autouse=True)
def isolated_settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("APP_DATA_DIR", str(data_dir))
    monkeypatch.setenv("APP_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("APP_CONFIG_DIR", str(Path("configs").resolve()))

    reset_settings_cache()
    reset_db_state()
    yield
    reset_settings_cache()
    reset_db_state()
