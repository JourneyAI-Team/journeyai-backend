import datetime as dt
import uuid
from typing import Optional

from beanie import Document
from pydantic import BaseModel, Field

from app.schemas.types import RoleType


class Profile(BaseModel):
    """
    User profile information that can be filled by users or assistants.

    Parameters
    ----------
    first_name : str, optional
        User's first name
    last_name : str, optional
        User's last name
    nickname : str, optional
        User's preferred nickname
    gender : str, optional
        User's gender identity
    birth_date : str, optional
        User's birth date in string format (e.g., "1990-01-15")
    bio : str, optional
        User's biography or description
    interests : list[str], optional
        List of user's interests or hobbies
    location : str, optional
        User's location or residence
    occupation : str, optional
        User's job title or occupation
    personality_traits : list[str], optional
        Personality traits identified by assistants or self-reported
    communication_style : str, optional
        Preferred communication style (e.g., "formal", "casual", "direct")
    goals : list[str], optional
        User's personal or professional goals
    preferences : dict, optional
        Key-value pairs for various user preferences
    assistant_notes : dict, optional
        Notes that assistants can add about the user (assistant_id -> notes)
    """

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    bio: Optional[str] = None
    interests: Optional[list[str]] = None
    location: Optional[str] = None
    occupation: Optional[str] = None
    personality_traits: Optional[list[str]] = None
    communication_style: Optional[str] = None
    goals: Optional[list[str]] = None
    preferences: Optional[dict] = None
    assistant_notes: Optional[dict] = None


class User(Document):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)

    email: str
    hashed_password: str
    access_token: str | None = None
    role: RoleType = Field(default=RoleType.MEMBER)

    # User profile information
    profile: Profile = Field(default_factory=Profile)

    created_at: dt.datetime = Field(
        default_factory=lambda: dt.datetime.now(dt.timezone.utc)
    )

    # Relations
    organization_id: str | None = None
