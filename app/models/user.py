import datetime as dt
import uuid

from beanie import Document
from pydantic import Field

from app.schemas.types import RoleType


class User(Document):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)

    email: str
    hashed_password: str
    role: RoleType = Field(default=RoleType.MEMBER)

    created_at: dt.datetime = Field(default_factory=dt.datetime.now(dt.timezone.utc))

    # Relations
    organization_id: str
