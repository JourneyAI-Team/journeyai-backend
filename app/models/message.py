import datetime as dt
import uuid

from beanie import Document, Insert, after_event
from pydantic import Field

from app.clients.arq_client import get_arq
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

    # Post Actions
    embed_after_insert: bool = Field(default=True, exclude=True)

    # Relations
    user_id: str
    organization_id: str
    session_id: str
    assistant_id: str
    account_id: str

    @after_event(Insert)
    async def post_message_creation(self):
        arq = await get_arq()
        await arq.enqueue_job(
            "post_message_creation",
            self.id,
            _queue_name="messages",
        )
