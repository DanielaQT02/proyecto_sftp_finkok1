from datetime import datetime
from decimal import Decimal

from pydantic import Field

from .base import SchemaBase


class InvoiceBase(SchemaBase):
    response_code: str | None = None
    message: str | None = None
    taxpayer_id: str | None = None
    rtaxpayer_id: str | None = None
    total: Decimal | None = None
    xml_timbrado: str | None = None
    uuid: str | None = None


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(InvoiceBase):
    pass


class InvoiceRead(InvoiceBase):
    id: int
    buffer_id: int | None = None
    business_id: int
    created_at: datetime
    updated_at: datetime


class InvoiceSummary(SchemaBase):
    total_invoices: int = 0
    success_count: int = 0
    error_count: int = 0
    success_rate: float = 0.0

Invoice = InvoiceRead