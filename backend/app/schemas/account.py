from .base import SchemaBase


class AccountBase(SchemaBase):
    user_id: int


class AccountCreate(AccountBase):
    account_name: str = "Principal"


class AccountRead(AccountBase):
    id: int

class AccountUpdate(SchemaBase):
    user_id: int | None = None
    account_name: str | None = None