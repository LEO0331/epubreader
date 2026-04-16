from __future__ import annotations

import hmac
from datetime import UTC, datetime

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp


class ApiKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, *, api_key: str, header_name: str = "X-API-Key"):
        super().__init__(app)
        self.api_key = api_key
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Keep health endpoint public for probes.
        if request.url.path == "/api/v1/health":
            return await call_next(request)

        presented = request.headers.get(self.header_name)
        if not presented or not hmac.compare_digest(presented, self.api_key):
            request_id = getattr(request.state, "request_id", None)
            return JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": "unauthorized",
                        "message": "Missing or invalid API key.",
                        "request_id": request_id,
                        "path": str(request.url.path),
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                },
            )

        return await call_next(request)
