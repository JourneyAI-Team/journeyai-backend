from typing import Optional
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
    title: str
    body: str
    is_parent: bool
    parent_id: str | None
    session_id: str


class ArtifactRead(ArtifactBase):
    """
    Schema for reading artifact data.

    Parameters
    -----
    id : str
        Artifact unique identifier
    type : str
    origin_type : OriginType
    title : str
    body : str
    is_parent : bool
    parent_id : str, optional
    """

    id: str
    type: str
    origin_type: OriginType
    title: str
    body: str
    is_parent: bool
    parent_id: str | None


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
