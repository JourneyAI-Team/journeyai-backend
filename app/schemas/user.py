from pydantic import BaseModel, EmailStr


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
    """

    email: EmailStr
    password: str
    organization_id: str | None = None


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
    """

    id: str
    email: EmailStr
    role: str
    organization_id: str | None = None
