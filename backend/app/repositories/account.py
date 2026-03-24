from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.account import Account
from app.models.user import User
from app.repositories.base import BaseRepository


class AccountRepository(BaseRepository[Account]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Account)

    async def get_by_user_id(self, user_id: int) -> Account | None:
        stmt = select(Account).where(Account.user_id == user_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def search_by_user_email(
        self,
        *,
        email: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Account]:
        email = email.strip()
        if not email:
            return []
        stmt = (
            select(Account)
            .join(User)
            .where(User.email.ilike(f"%{email}%"))
            .limit(limit)
            .offset(offset)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_with_businesses(self, account_id: int) -> Account | None:
        stmt = (
            select(Account)
            .where(Account.id == account_id)
            .options(selectinload(Account.businesses))
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()