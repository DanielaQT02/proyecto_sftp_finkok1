from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.business import Business
from app.repositories.base import BaseRepository


class BusinessRepository(BaseRepository[Business]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Business)

    async def list_by_account(self, account_id: int, limit: int = 50, offset: int = 0):
        stmt = (
            select(Business)
            .where(Business.account_id == account_id)
            .limit(limit)
            .offset(offset)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def get_by_taxpayer_id(self, taxpayer_id: str) -> Business | None:
        stmt = select(Business).where(Business.taxpayer_id == taxpayer_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()