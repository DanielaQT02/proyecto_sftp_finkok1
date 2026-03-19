
from .base import InputSchema, SchemaBase
from datetime import datetime
from pydantic import Field

class BusinessUpdate(SchemaBase):
    taxpayer_id: str | None = None
    business_name: str | None = None
    account_id: int | None = None

class BusinessStatistics(SchemaBase):
    business_id: int
    business_name: str
    taxpayer_id: str
    total_invoices: int
    stamped_success: int
    stamped_error: int
    success_rate: float


class BusinessBase(InputSchema):
    taxpayer_id: str = Field(..., min_length=1)
    business_name: str = Field(..., min_length=1)


class BusinessCreate(BusinessBase):
    pass


class BusinessRead(BusinessBase, SchemaBase):
    id: int
    account_id: int
    created_at: datetime