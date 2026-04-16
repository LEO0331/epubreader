from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from packages.core.config.settings import AppConfig, AppSettings, ModelsConfig, StorageConfig


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Config file must be a mapping: {path}")
    return loaded


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _resolve_config_dir(config_dir: str | None = None) -> Path:
    if config_dir is not None:
        return Path(config_dir).expanduser().resolve()

    from_env = os.getenv("APP_CONFIG_DIR")
    if from_env:
        return Path(from_env).expanduser().resolve()

    return Path("configs").resolve()


def _parse_csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def load_settings(config_dir: str | None = None) -> AppSettings:
    base_dir = _resolve_config_dir(config_dir)
    app_data = _read_yaml(base_dir / "app.yaml")

    app_cfg = AppConfig(**app_data.get("app", {}))
    storage_cfg = StorageConfig(**app_data.get("storage", {}))
    models_cfg = ModelsConfig(**app_data.get("models", {}))

    app_cfg = app_cfg.model_copy(
        update={
            "name": os.getenv("APP_NAME", app_cfg.name),
            "version": os.getenv("APP_VERSION", app_cfg.version),
            "env": os.getenv("APP_ENV", app_cfg.env),
            "host": os.getenv("APP_HOST", app_cfg.host),
            "port": int(os.getenv("APP_PORT", str(app_cfg.port))),
            "debug": _env_bool("APP_DEBUG", app_cfg.debug),
            "log_level": os.getenv("APP_LOG_LEVEL", app_cfg.log_level),
            "request_id_header": os.getenv("APP_REQUEST_ID_HEADER", app_cfg.request_id_header),
            "cors_allow_origins": (
                _parse_csv(os.environ["APP_CORS_ALLOW_ORIGINS"])
                if "APP_CORS_ALLOW_ORIGINS" in os.environ
                else app_cfg.cors_allow_origins
            ),
        }
    )

    storage_cfg = storage_cfg.model_copy(
        update={
            "database_url": os.getenv("APP_DATABASE_URL", storage_cfg.database_url),
            "data_dir": os.getenv("APP_DATA_DIR", storage_cfg.data_dir),
        }
    )

    models_cfg = models_cfg.model_copy(
        update={
            "profile": os.getenv("APP_MODELS_PROFILE", models_cfg.profile),
        }
    )

    model_provider = _read_yaml(base_dir / f"models.{models_cfg.profile}.yaml")

    return AppSettings(
        app=app_cfg,
        storage=storage_cfg,
        models=models_cfg,
        model_provider=model_provider,
        raw_config_dir=base_dir,
    )


_settings_cache: AppSettings | None = None


def get_settings() -> AppSettings:
    global _settings_cache
    if _settings_cache is None:
        _settings_cache = load_settings()
    return _settings_cache


def reset_settings_cache() -> None:
    global _settings_cache
    _settings_cache = None
