from time import perf_counter
from uuid import uuid4

import structlog
from fastapi import FastAPI, Request
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from .logger import log


def add_http_logging_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def log_requests(request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = uuid4().hex
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            path=request.url.path,
            method=request.method,
        )

        started_at = perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((perf_counter() - started_at) * 1000, 2)
            log.exception("http_request_failed", duration_ms=duration_ms)
            raise

        duration_ms = round((perf_counter() - started_at) * 1000, 2)
        log.info(
            "http_request_completed",
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        return response
