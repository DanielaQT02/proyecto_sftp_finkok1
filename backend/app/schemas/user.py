
from .base import SchemaBase
from datetime import datetime
from pydantic import EmailStr, field_validator

class UserUpdate(SchemaBase):
    email: str | None = None
    password: str | None = None
    role: str | None = None
    active: bool | None = None


class UserRead(SchemaBase):
    id: int
    email: EmailStr
    name: str
    role: str
    active: bool
    created_at: datetime

class UserCreate(SchemaBase):
    email: EmailStr
    name: str
    password: str
    role: str = "cliente"

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('La contraseña debe tener mínimo 8 caracteres')
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v