from datetime import datetime

from .base import SchemaBase


class BufferRead(SchemaBase):
    id: int
    batch_id: int
    xml_name: str
    status: str
    created_at: datetime