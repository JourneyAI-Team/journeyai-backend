import datetime as dt
import uuid

from beanie import Document
from pydantic import Field


class Organization(Document):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)

    name: str
    domain: str

    created_at: dt.datetime = Field(
        default_factory=lambda: dt.datetime.now(dt.timezone.utc)
    )

    # Relations
    owner_id: str | None = None
