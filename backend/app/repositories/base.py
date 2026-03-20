from typing import Any, Generic, TypeVar, Type, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

ModelT = TypeVar("ModelT")

class BaseRepository(Generic[ModelT]):
    def __init__(self, session: AsyncSession, model: Type[ModelT]):
        self.session = session
        self.model = model

    async def get(self, obj_id: Any) -> ModelT | None:
        return await self.session.get(self.model, obj_id)

    async def list(self, *, limit: int = 50, offset: int = 0) -> Sequence[ModelT]:
        stmt = select(self.model).limit(limit).offset(offset)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def create(self, data: dict) -> ModelT:
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj_id: Any, data: dict) -> ModelT | None:
        obj = await self.get(obj_id)
        if not obj:
            return None

        for k, v in data.items():
            setattr(obj, k, v)

        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj_id: Any) -> bool:
        obj = await self.get(obj_id)
        if not obj:
            return False
        self.session.delete(obj)
        await self.session.commit()
        return True