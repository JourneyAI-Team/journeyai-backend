import datetime as dt
import uuid

from beanie import Document
from pydantic import Field

from app.schemas.types import RoleType


class User(Document):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)

    email: str
    hashed_password: str
    access_token: str | None = None
    role: RoleType = Field(default=RoleType.MEMBER)

    created_at: dt.datetime = Field(
        default_factory=lambda: dt.datetime.now(dt.timezone.utc)
    )

    # Relations
    organization_id: str | None = None
