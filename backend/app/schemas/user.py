
from .base import SchemaBase
from datetime import datetime
from pydantic import EmailStr

class UserUpdate(SchemaBase):
    name: str | None = None
    password: str | None = None
    role: str | None = None


class UserRead(SchemaBase):
    id: int
    email: EmailStr
    role: str
    active: bool
    created_at: datetime

class UserCreate(SchemaBase):
    email: EmailStr
    password: str
    role: str = "cliente"