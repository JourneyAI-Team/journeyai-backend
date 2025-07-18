import datetime as dt
import uuid

from beanie import Document
from pydantic import Field


class Opportunity(Document):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)

    name: str
    amount: float
    stage: str

    created_at: dt.datetime = Field(
        default_factory=lambda: dt.datetime.now(dt.timezone.utc)
    )

    # Relations
    organization_id: str
    account_id: str
    user_id: str


class Contact(Document):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)

    email: str
    first_name: str
    last_name: str | None = None
    title: str | None = None

    # Relations
    organization_id: str
    account_id: str
    user_id: str
