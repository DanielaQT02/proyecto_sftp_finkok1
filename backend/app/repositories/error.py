from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.error import ErrorStamping
from app.repositories.base import BaseRepository


class ErrorStampingRepository(BaseRepository[ErrorStamping]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=ErrorStamping)

    async def list_by_buffer(self, buffer_id: int, limit: int = 50, offset: int = 0):
        stmt = (
            select(ErrorStamping)
            .where(ErrorStamping.buffer_id == buffer_id)
            .limit(limit)
            .offset(offset)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()