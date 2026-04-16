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
            "api_key": os.getenv("APP_API_KEY", app_cfg.api_key),
            "ingest_max_bytes": int(
                os.getenv("APP_INGEST_MAX_BYTES", str(app_cfg.ingest_max_bytes))
            ),
            "ocr_enabled": _env_bool("APP_OCR_ENABLED", app_cfg.ocr_enabled),
            "ocr_langs": os.getenv("APP_OCR_LANGS", app_cfg.ocr_langs),
            "ocr_min_text_chars": int(
                os.getenv("APP_OCR_MIN_TEXT_CHARS", str(app_cfg.ocr_min_text_chars))
            ),
            "ocr_tesseract_cmd": os.getenv("APP_OCR_TESSERACT_CMD", app_cfg.ocr_tesseract_cmd),
            "ocr_max_pages": int(os.getenv("APP_OCR_MAX_PAGES", str(app_cfg.ocr_max_pages))),
            "ocr_page_timeout_seconds": int(
                os.getenv(
                    "APP_OCR_PAGE_TIMEOUT_SECONDS",
                    str(app_cfg.ocr_page_timeout_seconds),
                )
            ),
            "ocr_total_timeout_seconds": int(
                os.getenv(
                    "APP_OCR_TOTAL_TIMEOUT_SECONDS",
                    str(app_cfg.ocr_total_timeout_seconds),
                )
            ),
            "ocr_isolate_worker": _env_bool("APP_OCR_ISOLATE_WORKER", app_cfg.ocr_isolate_worker),
            "ingest_host_allowlist_enabled": _env_bool(
                "APP_INGEST_HOST_ALLOWLIST_ENABLED",
                app_cfg.ingest_host_allowlist_enabled,
            ),
            "ingest_host_allowlist": (
                _parse_csv(os.environ["APP_INGEST_HOST_ALLOWLIST"])
                if "APP_INGEST_HOST_ALLOWLIST" in os.environ
                else app_cfg.ingest_host_allowlist
            ),
            "cors_allow_origins": (
                _parse_csv(os.environ["APP_CORS_ALLOW_ORIGINS"])
                if "APP_CORS_ALLOW_ORIGINS" in os.environ
                else app_cfg.cors_allow_origins
            ),
        }
    )
    if app_cfg.env.lower() not in {"local", "dev", "test"} and not app_cfg.api_key:
        raise ValueError("APP_API_KEY is required for non-local environments")

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
