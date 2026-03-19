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
    buffer_id: int | None = None
    created_at: datetime


class ErrorDetail(ErrorRead):
    business_name: str | None = None
    taxpayer_id: str | None = None
    total_amount: float | None = None


class ErrorSummary(SchemaBase):
    total_errors: int
    errors_by_code: dict[str, int] = {}
    errors_by_message: dict[str, int] = {}
    days: int


ErrorStamping = ErrorRead