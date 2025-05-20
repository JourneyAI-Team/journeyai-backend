from typing import List

from pydantic import BaseModel, Field


class InputMessageSchema(BaseModel):
    content: str
    attachments: List[str] = Field(default_factory=list)
