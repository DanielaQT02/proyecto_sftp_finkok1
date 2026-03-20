from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql.functions import count, sum as sql_sum
from datetime import datetime
from typing import Optional

from app.models.invoice import Invoice
from app.repositories.base import BaseRepository


class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Invoice)

    async def get_by_buffer(self, buffer_id: int) -> Invoice | None:
        stmt = select(Invoice).where(Invoice.buffer_id == buffer_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_by_uuid(self, uuid: str) -> Invoice | None:
        stmt = select(Invoice).where(Invoice.uuid == uuid)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_all_filtered(
        self,
        business_id: Optional[int] = None,
        taxpayer_id: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Invoice]:
        stmt = select(Invoice)
        if business_id is not None:
            stmt = stmt.where(Invoice.business_id == business_id)
        if taxpayer_id is not None:
            stmt = stmt.where(Invoice.taxpayer_id == taxpayer_id)
        if from_date is not None:
            stmt = stmt.where(Invoice.created_at >= from_date)
        if to_date is not None:
            stmt = stmt.where(Invoice.created_at <= to_date)
        if status is not None:
            if status == "success":
                stmt = stmt.where(Invoice.response_code == "S03")
            elif status == "error":
                stmt = stmt.where(Invoice.response_code.like("E%"))
            elif status == "pending":
                stmt = stmt.where(Invoice.response_code.is_(None))
        stmt = stmt.offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def get_statistics(self, business_id: Optional[int] = None) -> dict:
        stmt = select(
            count(Invoice.id).label("total_invoices"),
            sql_sum(Invoice.total).label("total_amount"),
            count(Invoice.id, filter_=Invoice.response_code == "S03").label("success_count"),
            count(Invoice.id, filter_=Invoice.response_code.like("E%")).label("error_count"),
            count(Invoice.id, filter_=Invoice.response_code.is_(None)).label("pending_count"),
        )
        if business_id is not None:
            stmt = stmt.where(Invoice.business_id == business_id)
        res = await self.session.execute(stmt)
        row = res.one()
        return {
            "total_invoices": row.total_invoices or 0,
            "total_amount": float(row.total_amount) if row.total_amount else 0.0,
            "success_count": row.success_count or 0,
            "error_count": row.error_count or 0,
            "pending_count": row.pending_count or 0,
            "success_rate": round((row.success_count or 0) / (row.total_invoices or 1) * 100, 2) if row.total_invoices else 0.0,
        }