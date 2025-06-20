from typing import Optional

from pydantic import BaseModel


class ProfileBase(BaseModel):
    """
    Base profile schema with common attributes
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
    favorite_assistants: Optional[list[str]] = None

class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
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
    favorite_assistants: Optional[list[str]] = None

class ProfileRead(ProfileBase):
    pass


class AssistantNotesUpdate(BaseModel):
    """
    Schema for updating assistant notes

    Parameters
    ----------
    notes : str
        The notes to add or update for the assistant
    """

    notes: str
