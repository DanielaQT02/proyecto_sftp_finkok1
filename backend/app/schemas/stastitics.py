from datetime import date, datetime

from .base import SchemaBase


class StampingStatisticsRead(SchemaBase):
    id: int
    business_id: int
    total_invoices: int
    stamped_success: int
    stamped_error: int
    validation_errors: int
    certificate_errors: int
    pac_errors: int
    period: date
    created_at: datetime