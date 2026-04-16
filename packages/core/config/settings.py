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
