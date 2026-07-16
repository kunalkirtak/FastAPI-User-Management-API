"""
Shared FastAPI dependencies used across multiple routers.

Keeping these separate from `database.py` (which only holds `get_db`) gives
each concern its own home as the app grows -- e.g. this is also where a
future `get_current_user` auth dependency would live.
"""

from dataclasses import dataclass

from fastapi import Query, Request


@dataclass
class PaginationParams:
    skip: int
    limit: int


def get_pagination_params(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Max number of records to return"),
) -> PaginationParams:
    """Reusable skip/limit pagination, injectable into any list endpoint."""
    return PaginationParams(skip=skip, limit=limit)


def get_request_id(request: Request) -> str:
    """
    Return the request id assigned by `RequestLoggingMiddleware`.

    Falls back to 'unknown' if the middleware isn't in the stack (e.g. a
    unit test that calls a route function directly rather than going
    through the full ASGI app).
    """
    return getattr(request.state, "request_id", "unknown")
