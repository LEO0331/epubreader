from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from packages.core.config.loader import get_settings
from packages.storage.db.base import Base

_ENGINE: Engine | None = None
_SESSION_FACTORY: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    global _ENGINE
    if _ENGINE is None:
        settings = get_settings()
        db_url = settings.storage.database_url
        connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
        _ENGINE = create_engine(db_url, echo=False, future=True, connect_args=connect_args)
    return _ENGINE


def get_session_factory() -> sessionmaker[Session]:
    global _SESSION_FACTORY
    if _SESSION_FACTORY is None:
        _SESSION_FACTORY = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)
    return _SESSION_FACTORY


def init_db() -> None:
    from packages.storage.db import models as _models  # noqa: F401

    Base.metadata.create_all(bind=get_engine())


def reset_db_state() -> None:
    global _ENGINE
    global _SESSION_FACTORY
    _ENGINE = None
    _SESSION_FACTORY = None


def get_db_session() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
