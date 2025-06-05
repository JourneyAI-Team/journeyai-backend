from typing import Optional

from pydantic import BaseModel, EmailStr

from app.schemas.profile import ProfileCreate, ProfileRead


class UserBase(BaseModel):
    """
    Base user schema with common attributes
    """

    email: EmailStr


class UserCreate(UserBase):
    """
    Schema for user creation/registration

    Parameters
    ----------
    email : EmailStr
        User's email address, used for login
    password : str
        User's plain text password that will be hashed
    organization_id : str, optional
        ID of the organization the user belongs to
    profile : ProfileCreate, optional
        User's profile information
    """

    email: EmailStr
    password: str
    organization_id: str | None = None
    profile: Optional[ProfileCreate] = None


class UserRead(UserBase):
    """
    Schema for reading user data

    Parameters
    ----------
    id : str
        User's unique identifier
    email : EmailStr
        User's email address
    role : str
        User's role in the system
    organization_id : str, optional
        ID of the organization the user belongs to
    profile : ProfileRead
        User's profile information
    """

    id: str
    email: EmailStr
    role: str
    organization_id: str | None = None
    profile: ProfileRead


class UserApiKey(BaseModel):
    """
    Schema for user API key
    """

    api_key: str
