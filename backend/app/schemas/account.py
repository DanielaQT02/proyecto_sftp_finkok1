from .base import SchemaBase


class AccountBase(SchemaBase):
    user_id: int


class AccountCreate(AccountBase):
    pass


class AccountRead(AccountBase):
    id: int