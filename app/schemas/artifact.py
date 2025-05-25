import datetime as dt

from pydantic import BaseModel

from app.schemas.types import OriginType


class ArtifactBase(BaseModel):
    """
    Artifact base schema with common attributes
    """

    type: str
    origin_type: OriginType
    title: str
    body: str


class ArtifactCreate(ArtifactBase):
    """
    Schema for creating an artifact.
    """

    is_parent: bool = False

    # Relations
    parent_id: str | None = None
    session_id: str | None = None

    # Scoping
    account_id: str | None = None


class ArtifactUpdate(ArtifactBase):
    """
    Schema for updating an artifact.
    """

    account_id: str | None = None


class ArtifactRead(ArtifactBase):
    id: str

    is_parent: bool
    created_at: dt.datetime

    user_id: str
    organization_id: str
    session_id: str | None
    parent_id: str | None
    account_id: str
