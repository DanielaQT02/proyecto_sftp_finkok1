from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.statistics import StampingStatistics
from app.repositories.base import BaseRepository


class StampingStatisticsRepository(BaseRepository[StampingStatistics]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=StampingStatistics)

    async def list_by_business(self, business_id: int, limit: int = 50, offset: int = 0):
        stmt = (
            select(StampingStatistics)
            .where(StampingStatistics.business_id == business_id)
            .order_by(StampingStatistics.period.desc())
            .limit(limit)
            .offset(offset)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def get_by_business_and_period(self, business_id: int, period):
        stmt = select(StampingStatistics).where(
            StampingStatistics.business_id == business_id,
            StampingStatistics.period == period,
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()