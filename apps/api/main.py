from __future__ import annotations

from fastapi import APIRouter, FastAPI

from apps.api.errors import register_exception_handlers
from apps.api.lifespan import lifespan
from apps.api.middleware.request_id import RequestIdMiddleware
from apps.api.routes.health import router as health_router
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
    app.include_router(api_router)

    return app


app = create_app()
