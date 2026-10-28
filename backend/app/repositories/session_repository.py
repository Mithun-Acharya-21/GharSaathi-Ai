from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.session import Session


class SessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, session_obj: Session) -> Session:
        self.session.add(session_obj)
        await self.session.commit()
        await self.session.refresh(session_obj)
        return session_obj

    async def get_by_id(self, session_id: str) -> Session | None:
        query = (
            select(Session).where(Session.id == session_id).options(selectinload(Session.activity))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id_with_attempts(self, session_id: str) -> Session | None:
        query = (
            select(Session)
            .where(Session.id == session_id)
            .options(selectinload(Session.attempts), selectinload(Session.activity))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_token_hash(self, token_hash: str) -> Session | None:
        query = (
            select(Session)
            .where(Session.session_token_hash == token_hash)
            .options(selectinload(Session.activity))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, session_obj: Session) -> None:
        await self.session.delete(session_obj)
        await self.session.commit()
