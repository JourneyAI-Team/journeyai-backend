from pydantic import BaseModel

from app.schemas.types import OriginType


class ArtifactBase(BaseModel):
    """
    Artifact base schema with common attributes
    """

    title: str
    body: str


class ArtifactCreate(ArtifactBase):
    """
    Schema for creating an artifact.

    Parameters
    -----
    type : str
    origin_type : OriginType
    title : str
    body : str
    is_parent : bool
    parent_id : str, optional
    session_id : str
    """

    type: str
    origin_type: OriginType
    is_parent: bool = False
    parent_id: str | None = None
    session_id: str


class ArtifactUpdate(ArtifactBase):
    """
    Schema for updating an artifact.

    Parameters
    -----
    type : str
    origin_type : OriginType
    title : str
    body : str
    """

    type: str
    origin_type: OriginType
    title: str
    body: str
