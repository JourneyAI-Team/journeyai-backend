import uuid

from beanie import Document
from pydantic import Field


class Session(Document):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)

    title: str = "New Session"
    summary: str | None = None

    # Relations
    user_id: str
    organization_id: str
    assistant_id: str
    account_id: str
