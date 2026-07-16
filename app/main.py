"""
Application entrypoint.

Creates the FastAPI app instance, wires up middleware, global exception
handlers, and includes the API routers. Run with:

    uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.database import Base, engine
from app.middleware.request_logger import RequestLoggingMiddleware
from app.utils.logger import get_logger, setup_logging

# Importing the models module registers every model's table on Base.metadata
# so that `Base.metadata.create_all()` below knows what to create. This
# import is required even though `models` isn't referenced directly here.
from app import models  # noqa: F401
from app.routers import health, users

# --------------------------------------------------------------------------------------
# Logging must be configured before anything else logs -- including the
# `create_all()` call below, whose SQL echo (if DEBUG=True) is routed
# through the logging module.
# --------------------------------------------------------------------------------------
setup_logging()
logger = get_logger(__name__)

# --------------------------------------------------------------------------------------
# Create database tables.
#
# For a project this size, creating tables directly from the models is fine
# for local development. Schema *changes* to an existing database should go
# through Alembic migrations instead (added in Part 4) so upgrades are
# tracked and reversible.
# --------------------------------------------------------------------------------------
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

# --------------------------------------------------------------------------------------
# Middleware
#
# Middleware added later wraps middleware added earlier, so CORS headers end
# up applied to every response -- including ones that error out inside the
# request-logging middleware.
# --------------------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)


# --------------------------------------------------------------------------------------
# Global exception handlers
# --------------------------------------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Log request-validation failures (bad/missing fields) with the request id
    for correlation, while preserving FastAPI's normal 422 response body so
    API consumers see no change in behavior.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(
        "validation error | id=%s | %s %s | %s",
        request_id, request.method, request.url.path, exc.errors(),
    )
    # Pydantic v2 error dicts can include a raw exception object under
    # `ctx.error` (e.g. from a failed `field_validator`), which the default
    # JSON encoder can't serialize. `jsonable_encoder` converts it safely.
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": jsonable_encoder(exc.errors())},
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """
    Defense-in-depth safety net: `user_service` already checks for duplicate
    emails/usernames before inserting, but a database-level unique
    constraint is the real source of truth under concurrent requests. If two
    requests race past the service-layer check at the same moment, the
    database rejects the second insert and this handler turns that into a
    clean 409 instead of a raw 500.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        "database integrity error | id=%s | %s %s | %s",
        request_id, request.method, request.url.path, str(exc.orig),
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "A record with these details already exists."},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Catch-all for anything not already handled above (or by FastAPI's
    built-in HTTPException handling). Logs the full traceback server-side
    but never leaks internal details to the client.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception(
        "unhandled exception | id=%s | %s %s", request_id, request.method, request.url.path
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


# --------------------------------------------------------------------------------------
# Routers
# --------------------------------------------------------------------------------------
# Resource routers are mounted under the versioned API prefix (e.g.
# /api/v1/users) so the API can introduce breaking changes in a future
# /api/v2 without disrupting existing clients. Infrastructure endpoints like
# /health stay unversioned, since orchestrators expect them at a fixed path.
app.include_router(health.router)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Root"])
def read_root():
    """Simple welcome endpoint confirming the API is running."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "redoc": "/redoc",
    }
