from __future__ import annotations

from datetime import UTC, datetime

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def _error_payload(
    *,
    code: str,
    message: str,
    request_id: str | None,
    path: str,
) -> dict[str, dict[str, str | None]]:
    return {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
            "path": path,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:  # noqa: ARG001
        request_id = getattr(request.state, "request_id", None)
        payload = _error_payload(
            code="internal_error",
            message="An unexpected error occurred.",
            request_id=request_id,
            path=str(request.url.path),
        )
        return JSONResponse(status_code=500, content=payload)
