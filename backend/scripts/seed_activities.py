import asyncio
import logging
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.db.session import close_db_engine, get_sessionmaker
from app.models.activity import Activity
from app.seed.activities import SEED_ACTIVITIES

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")
logger = logging.getLogger("seed")


async def seed_activities() -> None:
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        created_count = 0
        existing_count = 0
        for act_data in SEED_ACTIVITIES:
            stmt = select(Activity).where(Activity.id == act_data["id"])
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing is None:
                activity = Activity(**act_data)
                session.add(activity)
                created_count += 1
                logger.info(
                    "Created activity for Grade %d: %s", act_data["grade"], act_data["topic"]
                )
            else:
                existing_count += 1
                logger.info(
                    "Activity for Grade %d already exists (id=%s), skipping to prevent overwrite.",
                    act_data["grade"],
                    act_data["id"],
                )

        await session.commit()
        logger.info("Seeding complete. Created: %d, Existing: %d.", created_count, existing_count)

    await close_db_engine()


if __name__ == "__main__":
    asyncio.run(seed_activities())
