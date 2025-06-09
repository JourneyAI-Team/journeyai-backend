import datetime as dt

from pydantic import BaseModel
from typing_extensions import NotRequired, TypedDict

from app.schemas.types import SenderType


class IngestMessageSchema(TypedDict):
    content: str
    attachments: NotRequired[list[str]]

    session_id: str


class InputMessageSchema(TypedDict):
    content: str


class MessageRead(BaseModel):
    """Schema for reading message data from the API."""

    id: str
    output: dict | None = None
    input: InputMessageSchema | None = None
    sender: SenderType
    created_at: dt.datetime
    user_id: str
    organization_id: str
    session_id: str
    assistant_id: str
    account_id: str
