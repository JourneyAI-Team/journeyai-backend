import datetime as dt
import uuid

from beanie import Document
from pydantic import Field


class Assistant(Document):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)

    name: str
    internal_name: str
    description: str
    developer_prompt: str
    tool_config: dict[str, str]
    testing: bool
    version: str

    created_at: dt.datetime = Field(
        default_factory=lambda: dt.datetime.now(dt.timezone.utc)
    )

    # Relations
    organization_id: str
