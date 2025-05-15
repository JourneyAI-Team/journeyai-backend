import datetime as dt
import uuid

from beanie import Document
from pydantic import Field


class Account(Document):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)

    name: str
    description: str | None = None
    created_at: dt.datetime = Field(
        default_factory=lambda: dt.datetime.now(dt.timezone.utc)
    )

    # Relations
    organization_id: str
    user_id: str
