from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.invoice import Invoice
from app.repositories.base import BaseRepository


class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Invoice)

    async def get_by_buffer(self, buffer_id: int) -> Invoice | None:
        stmt = select(Invoice).where(Invoice.buffer_id == buffer_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()