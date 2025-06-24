import datetime as dt

from pydantic import BaseModel
from typing_extensions import NotRequired, TypedDict

from app.schemas.types import SenderType


class AttachmentMetadata(BaseModel):
    """Schema for message attachment metadata.

    Parameters
    ----------
    type : str
        The type of attachment, defaults to "file"
    name : str | None
        The name of the file, if available
    mimetype : str | None
        The MIME type of the file, if available
    size : int | None
        The size of the file in bytes, if available
    """

    type: str = "file"
    name: str | None = None
    mimetype: str | None = None
    size: int | None = None


class IngestMessageSchema(TypedDict):
    content: str
    attachments: NotRequired[list[AttachmentMetadata]]

    session_id: str


class InputMessageSchema(TypedDict):
    content: str


class MessageRead(BaseModel):
    """Schema for reading message data from the API."""

    id: str
    output: dict | None = None
    input: InputMessageSchema | None = None
    sender: SenderType
    attachments: list[AttachmentMetadata] = []
    created_at: dt.datetime
    user_id: str
    organization_id: str
    session_id: str
    assistant_id: str
    account_id: str
