from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.batch import StampingBatch
from app.repositories.base import BaseRepository


class StampingBatchRepository(BaseRepository[StampingBatch]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=StampingBatch)

    async def list_by_business(self, business_id: int, limit: int = 50, offset: int = 0):
        stmt = (
            select(StampingBatch)
            .where(StampingBatch.business_id == business_id)
            .limit(limit)
            .offset(offset)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def list_by_business_ids(self, business_ids: list[int], limit: int = 50, offset: int = 0):
        if not business_ids:
            return []
        stmt = (
            select(StampingBatch)
            .where(StampingBatch.business_id.in_(business_ids))
            .limit(limit)
            .offset(offset)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def get_with_buffers(self, batch_id: int) -> StampingBatch | None:
        stmt = (
            select(StampingBatch)
            .where(StampingBatch.id == batch_id)
            .options(selectinload(StampingBatch.buffers))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()