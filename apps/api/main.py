from __future__ import annotations

from fastapi import APIRouter, FastAPI

from apps.api.errors import register_exception_handlers
from apps.api.lifespan import lifespan
from apps.api.middleware.request_id import RequestIdMiddleware
from apps.api.routes.artifacts import router as artifacts_router
from apps.api.routes.books import router as books_router
from apps.api.routes.health import router as health_router
from apps.api.routes.ingest import router as ingest_router
from apps.api.routes.jobs import router as jobs_router
from apps.api.routes.query import router as query_router
from packages.core.config.loader import get_settings
from packages.core.logging.logger import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.app.log_level)

    app = FastAPI(title=settings.app.name, version=settings.app.version, lifespan=lifespan)
    app.add_middleware(RequestIdMiddleware, header_name=settings.app.request_id_header)
    register_exception_handlers(app)

    api_router = APIRouter(prefix="/api/v1")
    api_router.include_router(health_router)
    api_router.include_router(ingest_router)
    api_router.include_router(jobs_router)
    api_router.include_router(books_router)
    api_router.include_router(artifacts_router)
    api_router.include_router(query_router)
    app.include_router(api_router)

    return app


app = create_app()
