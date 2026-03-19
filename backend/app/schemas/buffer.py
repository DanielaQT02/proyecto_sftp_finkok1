
from .base import SchemaBase
from datetime import datetime

class BufferCreate(SchemaBase):
    batch_id: int
    xml_name: str
    status: str = "pending"


class BufferRead(SchemaBase):
    id: int
    batch_id: int
    xml_name: str
    status: str
    created_at: datetime