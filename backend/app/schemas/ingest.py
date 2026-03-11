from typing import List

from pydantic import BaseModel, Field


class BatchIngestRequest(BaseModel):
    xml_names: List[str] = Field(
        ...,
        min_length=1,
        description="Lista de nombres de XML dentro del ZIP",
    )