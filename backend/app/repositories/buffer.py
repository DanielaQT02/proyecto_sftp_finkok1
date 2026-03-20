from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.buffer import Buffer
from app.repositories.base import BaseRepository


class BufferRepository(BaseRepository[Buffer]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Buffer)

    async def list_by_batch(self, batch_id: int, limit: int = 50, offset: int = 0):
        stmt = (
            select(Buffer)
            .where(Buffer.batch_id == batch_id)
            .limit(limit)
            .offset(offset)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def existing_names_by_batch(self, batch_id: int) -> set[str]:
        stmt = select(Buffer.xml_name).where(Buffer.batch_id == batch_id)
        res = await self.session.execute(stmt)
        return {row[0] for row in res.all() if row[0]}

    async def create_many(
        self,
        batch_id: int,
        xml_names: list[str],
        default_status: str = "pending",
    ) -> list[Buffer]:
        objs = [
            Buffer(batch_id=batch_id, xml_name=name, status=default_status)
            for name in xml_names
        ]
        self.session.add_all(objs)
        return objs

    async def get_with_details(self, buffer_id: int) -> Buffer | None:
        stmt = (
            select(Buffer)
            .where(Buffer.id == buffer_id)
            .options(
                selectinload(Buffer.invoices),
                selectinload(Buffer.errors)
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()