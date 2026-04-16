from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    name: str = "book-qa-library"
    version: str = "0.1.0"
    env: str = "local"
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
    log_level: str = "INFO"
    request_id_header: str = "X-Request-ID"
    cors_allow_origins: list[str] = Field(default_factory=list)
    api_key: str | None = None
    ingest_max_bytes: int = 50 * 1024 * 1024
    ocr_enabled: bool = True
    ocr_langs: str = "chi_tra+eng"
    ocr_min_text_chars: int = 80
    ocr_tesseract_cmd: str | None = None
    ocr_max_pages: int = 0
    ocr_page_timeout_seconds: int = 0
    ocr_total_timeout_seconds: int = 0
    ocr_isolate_worker: bool = False
    ingest_host_allowlist_enabled: bool = False
    ingest_host_allowlist: list[str] = Field(default_factory=list)


class StorageConfig(BaseModel):
    database_url: str = "sqlite:///./data/app.db"
    data_dir: str = "./data"


class ModelsConfig(BaseModel):
    profile: str = "local"


class AppSettings(BaseModel):
    app: AppConfig = Field(default_factory=AppConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    models: ModelsConfig = Field(default_factory=ModelsConfig)
    model_provider: dict[str, Any] = Field(default_factory=dict)
    raw_config_dir: Path
