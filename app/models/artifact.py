import datetime as dt
import uuid

from beanie import Document
from pydantic import Field

from app.schemas.types import OriginType


class Artifact(Document):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)

    type: str
    origin_type: OriginType
    title: str
    body: str
    is_parent: bool = False
    created_at: dt.datetime = Field(
        default_factory=lambda: dt.datetime.now(dt.timezone.utc)
    )

    # Relations
    user_id: str
    organization_id: str
    session_id: str | None = None  # Exists if artifact is created from within a session
    parent_id: str | None = None
    artifact_id: str | None = None

    # Scoping
    account_id: str | None = (
        None  # This can be None if the Artifact is a assistant document
    )
