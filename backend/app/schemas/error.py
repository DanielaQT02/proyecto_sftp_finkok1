from datetime import datetime

from .base import SchemaBase


class ErrorBase(SchemaBase):
    response_code: str | None = None
    error_message: str
    error_stage: str | None = None


class ErrorCreate(ErrorBase):
    pass


class ErrorRead(ErrorBase):
    id: int
    buffer_id: int
    occurred_at: datetime