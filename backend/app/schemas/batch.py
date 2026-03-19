
from .base import InputSchema, SchemaBase
from datetime import datetime
from pydantic import Field

class BatchUpdate(SchemaBase):
    business_id: int | None = None
    zip_name: str | None = None
    total_xml: int | None = None
    status: str | None = None
    task_id: str | None = None


class BatchBase(InputSchema):
    business_id: int
    zip_name: str = Field(..., min_length=1)
    total_xml: int = 0
    status: str = "pending"
    task_id: str | None = None


class BatchCreate(BatchBase):
    pass


class BatchRead(BatchBase, SchemaBase):
    id: int
    created_at: datetime