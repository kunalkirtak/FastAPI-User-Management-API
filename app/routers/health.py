"""
Health check endpoint.

Intended for load balancers / container orchestrators (e.g. Kubernetes
liveness & readiness probes, or a simple uptime monitor) -- it reports
whether the service is up *and* whether it can actually reach its database.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.utils.helpers import utcnow
from app.utils.logger import get_logger

router = APIRouter(tags=["Health"])
logger = get_logger(__name__)


@router.get("/health", summary="Health check")
def health_check(db: Session = Depends(get_db)):
    """
    Return service health.

    - `status: "ok"` and HTTP 200 when the database is reachable.
    - `status: "degraded"` and HTTP 503 when it isn't -- this lets an
      orchestrator automatically stop routing traffic to this instance.
    """
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unreachable"
        logger.exception("health check: database is unreachable")

    payload = {
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": utcnow().isoformat(),
    }
    status_code = (
        status.HTTP_200_OK if db_status == "ok" else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    return JSONResponse(content=payload, status_code=status_code)
