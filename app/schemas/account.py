import datetime as dt

from pydantic import BaseModel


class AccountBase(BaseModel):
    """
    Base account schema with common attributes.
    """

    name: str


class AccountCreate(AccountBase):
    """
    Schema for creating an account under an organization.
    """

    description: str | None = None


class AccountRead(AccountBase):
    """
    Schema for reading account data.
    """

    id: str

    description: str | None = None
    created_at: dt.datetime

    organization_id: str
    user_id: str


class AccountUpdate(BaseModel):
    """
    Schema for updating account. Only account name and description can be updated for now.
    """

    name: str | None = None
    description: str | None = None
