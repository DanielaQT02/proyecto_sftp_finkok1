from datetime import datetime

from .base import SchemaBase
from .error import ErrorRead
from .invoice import InvoiceRead


class BufferResultRead(SchemaBase):
    id: int
    batch_id: int
    xml_name: str
    status: str
    created_at: datetime
    invoice: InvoiceRead | None = None
    errors: list[ErrorRead] = []


class BatchResultsRead(SchemaBase):
    batch_id: int
    business_id: int
    zip_name: str
    total_xml: int
    task_id: str | None = None
    status: str
    created_at: datetime
    buffers: list[BufferResultRead] = []