from datetime import datetime

from pydantic import Field

from .base import InputSchema, SchemaBase


class BusinessBase(InputSchema):
    taxpayer_id: str = Field(..., min_length=1)
    business_name: str = Field(..., min_length=1)


class BusinessCreate(BusinessBase):
    pass


class BusinessRead(BusinessBase, SchemaBase):
    id: int
    account_id: int
    created_at: datetime