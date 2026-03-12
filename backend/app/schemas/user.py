class UserUpdate(SchemaBase):
    name: str | None = None
    password: str | None = None
    role: str | None = None
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

class UserCreate(SchemaBase):
    email: EmailStr
    name: str | None = None
    password: str
    role: str = "cliente"