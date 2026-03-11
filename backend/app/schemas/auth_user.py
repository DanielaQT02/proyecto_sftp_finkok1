from pydantic import BaseModel, EmailStr
from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate


class UserRead(BaseUser[int]):
    name: str | None = None
    role: str


class UserCreate(BaseUserCreate):
    email: EmailStr
    name: str | None = None
    password: str
    role: str = "user"


class UserUpdate(BaseUserUpdate):
    name: str | None = None
    role: str | None = None


class UserMe(BaseModel):
    id: int
    email: EmailStr
    name: str | None = None
    role: str
    is_active: bool
    is_superuser: bool
    is_verified: bool