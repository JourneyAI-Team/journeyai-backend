import datetime as dt
import uuid

from beanie import Document
from pydantic import Field

from app.schemas.message import InputMessageSchema
from app.schemas.types import SenderType


class Message(Document):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)

    output: dict | None = None
    input: InputMessageSchema | None = None
    sender: SenderType

    created_at: dt.datetime = Field(
        default_factory=lambda: dt.datetime.now(dt.timezone.utc)
    )

    # Relations
    user_id: str
    organization_id: str
    session_id: str
    assistant_id: str
    account_id: str
