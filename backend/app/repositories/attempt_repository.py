from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.enums import EvaluationStatus
from app.models.activity import Activity
from app.models.attempt import Attempt
from app.models.session import Session


class AttemptRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, attempt_obj: Attempt) -> Attempt:
        self.session.add(attempt_obj)
        await self.session.commit()
        await self.session.refresh(attempt_obj)
        return attempt_obj

    async def get_by_id(self, attempt_id: str) -> Attempt | None:
        query = (
            select(Attempt)
            .where(Attempt.id == attempt_id)
            .options(selectinload(Attempt.session).selectinload(Session.activity))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def count_for_session(self, session_id: str) -> int:
        query = select(func.count(Attempt.id)).where(Attempt.session_id == session_id)
        result = await self.session.execute(query)
        return result.scalar_one() or 0

    async def get_review_queue(self, grade: int | None = None) -> Sequence[Attempt]:
        query = (
            select(Attempt)
            .join(Session, Attempt.session_id == Session.id)
            .join(Activity, Session.activity_id == Activity.id)
            .where(Attempt.evaluation_status == EvaluationStatus.REVIEW_REQUIRED.value)
            .options(selectinload(Attempt.session).selectinload(Session.activity))
        )
        if grade is not None:
            query = query.where(Activity.grade == grade)

        query = query.order_by(Attempt.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()
