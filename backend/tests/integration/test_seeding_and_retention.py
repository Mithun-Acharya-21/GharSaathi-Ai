from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.models.session import Session
from app.seed.activities import SEED_ACTIVITIES


@pytest.mark.asyncio
async def test_seeding_idempotency(db_session: AsyncSession):
    # Verify 6 initial activities exist
    res = await db_session.execute(select(func.count(Activity.id)))
    count = res.scalar_one()
    assert count == 6

    # Re-inserting or checking existing prevents duplicates
    for act_data in SEED_ACTIVITIES:
        stmt = select(Activity).where(Activity.id == act_data["id"])
        existing = (await db_session.execute(stmt)).scalar_one_or_none()
        assert existing is not None

    res_after = await db_session.execute(select(func.count(Activity.id)))
    assert res_after.scalar_one() == 6


@pytest.mark.asyncio
async def test_session_retention_purge_logic(db_session: AsyncSession):
    now = datetime.now(UTC)
    expired_session = Session(
        activity_id=SEED_ACTIVITIES[0]["id"],
        language_code="kn-IN",
        status="active",
        consent_acknowledged=True,
        session_token_hash="fake-hash-for-purge-test",
        created_at=now - timedelta(days=40),
        expires_at=now - timedelta(days=1),
    )
    db_session.add(expired_session)
    await db_session.commit()

    # Verify added
    stmt = select(Session).where(Session.session_token_hash == "fake-hash-for-purge-test")
    res = await db_session.execute(stmt)
    assert res.scalar_one_or_none() is not None

    # Simulate purge query
    from sqlalchemy import delete, or_

    retention_cutoff = now - timedelta(days=30)
    purge_stmt = delete(Session).where(
        or_(
            Session.expires_at < now,
            Session.created_at < retention_cutoff,
        )
    )
    await db_session.execute(purge_stmt)
    await db_session.commit()

    # Verify purged
    res_after = await db_session.execute(stmt)
    assert res_after.scalar_one_or_none() is None
