from typing import List

from pydantic import BaseModel


class InputMessageSchema(BaseModel):
    content: str
    attachments: List[str]
