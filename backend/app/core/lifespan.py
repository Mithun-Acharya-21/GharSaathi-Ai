import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import close_db_engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    setup_logging(settings.LOG_LEVEL)
    logger.info("Starting up %s (env=%s)...", settings.APP_NAME, settings.APP_ENV)

    # Validate production guards
    settings.validate_runtime_guards()

    # Reusable shared HTTPX AsyncClient for external Gnani APIs
    limits = httpx.Limits(max_keepalive_connections=20, max_connections=50)
    timeout = httpx.Timeout(timeout=settings.GNANI_STT_TIMEOUT_SECONDS)
    app.state.http_client = httpx.AsyncClient(limits=limits, timeout=timeout)

    yield

    # Graceful shutdown
    logger.info("Shutting down %s...", settings.APP_NAME)
    if hasattr(app.state, "http_client") and app.state.http_client is not None:
        await app.state.http_client.aclose()

    await close_db_engine()
    logger.info("Shutdown complete.")
