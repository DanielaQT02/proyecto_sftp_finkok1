from pydantic import BaseModel, ConfigDict


class SchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class InputSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)