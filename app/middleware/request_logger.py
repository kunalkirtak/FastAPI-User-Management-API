"""
Request logging middleware.

For every request, this middleware:
    1. Assigns a request id (reusing an incoming `X-Request-ID` header if the
       client already supplied one, e.g. from an upstream gateway).
    2. Stores it on `request.state.request_id` so route handlers and
       exception handlers can include it in their own log lines.
    3. Times the request and logs one line when it starts and one when it
       finishes (or fails), including the status code and duration.
    4. Echoes the request id back as a response header, so a client (or a
       developer looking at browser dev tools) can correlate a response with
       server-side logs.
"""

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.utils.helpers import generate_request_id
from app.utils.logger import get_logger

logger = get_logger("app.request")

REQUEST_ID_HEADER = "X-Request-ID"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get(REQUEST_ID_HEADER) or generate_request_id()
        request.state.request_id = request_id

        client_host = request.client.host if request.client else "unknown"
        start_time = time.perf_counter()

        logger.info(
            "request started  | id=%s | %s %s | client=%s",
            request_id, request.method, request.url.path, client_host,
        )

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.exception(
                "request failed   | id=%s | %s %s | %.2fms",
                request_id, request.method, request.url.path, duration_ms,
            )
            raise

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "request finished | id=%s | %s %s | status=%s | %.2fms",
            request_id, request.method, request.url.path, response.status_code, duration_ms,
        )

        response.headers[REQUEST_ID_HEADER] = request_id
        response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"
        return response
