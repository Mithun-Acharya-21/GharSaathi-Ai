import asyncio
import logging
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import delete, or_

from app.core.config import get_settings
from app.db.session import close_db_engine, get_sessionmaker
from app.models.session import Session

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")
logger = logging.getLogger("purge")


async def purge_expired_sessions() -> None:
    settings = get_settings()
    now = datetime.now(UTC)
    retention_cutoff = now - timedelta(days=settings.DATA_RETENTION_DAYS)

    session_factory = get_sessionmaker()
    async with session_factory() as session:
        # Delete expired sessions OR sessions older than retention cutoff
        stmt = delete(Session).where(
            or_(
                Session.expires_at < now,
                Session.created_at < retention_cutoff,
            )
        )
        result = await session.execute(stmt)
        await session.commit()
        logger.info(
            "Purged %d expired or retained learning sessions and related attempts.", result.rowcount
        )

    await close_db_engine()


if __name__ == "__main__":
    asyncio.run(purge_expired_sessions())
