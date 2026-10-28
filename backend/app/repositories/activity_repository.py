from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity


class ActivityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, activity_id: str, published_only: bool = True) -> Activity | None:
        query = select(Activity).where(Activity.id == activity_id)
        if published_only:
            query = query.where(Activity.published.is_(True))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_filter(
        self,
        grade: int | None = None,
        language_code: str | None = None,
        published_only: bool = True,
    ) -> Sequence[Activity]:
        query = select(Activity)
        if published_only:
            query = query.where(Activity.published.is_(True))
        if grade is not None:
            query = query.where(Activity.grade == grade)
        if language_code is not None:
            query = query.where(Activity.language_code == language_code)
        query = query.order_by(Activity.grade, Activity.topic)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count_published(self, grade: int | None = None) -> int:
        query = select(Activity).where(Activity.published.is_(True))
        if grade is not None:
            query = query.where(Activity.grade == grade)
        result = await self.session.execute(query)
        return len(result.scalars().all())
