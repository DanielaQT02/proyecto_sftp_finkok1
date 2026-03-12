from datetime import datetime
from .base import SchemaBase

class StampingStatisticsCreate(SchemaBase):
    business_id: int
    period: str
    total_invoices: int = 0
    stamped_success: int = 0
    stamped_error: int = 0
    validation_errors: int = 0
    certificate_errors: int = 0
    pac_errors: int = 0

class StampingStatisticsRead(SchemaBase):
    id: int
    business_id: int
    total_invoices: int
    stamped_success: int
    stamped_error: int
    validation_errors: int
    certificate_errors: int
    pac_errors: int
    period: str
    created_at: datetime
