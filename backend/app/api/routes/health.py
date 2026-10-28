from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_db

router = APIRouter(tags=["Health"])


@router.get("/healthz", summary="Liveness check")
async def healthz():
    """Returns application liveness without exposing sensitive configuration."""
    return {"status": "ok", "app": "GharSaathi Maths API"}


@router.get("/readyz", summary="Readiness check")
async def readyz(
    response: Response,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Checks database connectivity. Does not call third-party Gnani APIs on each check."""
    checks = {
        "database": "unknown",
        "app_env": settings.APP_ENV,
    }

    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ready"
        return {"status": "ready", "checks": checks}
    except Exception:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        checks["database"] = "unavailable"
        return {"status": "not_ready", "checks": checks, "error": "Database connection failed"}
