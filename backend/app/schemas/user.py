from datetime import datetime

from pydantic import EmailStr

from .base import SchemaBase


class UserRead(SchemaBase):
    id: int
    email: EmailStr
    name: str | None = None
    role: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
    created_at: datetime