import datetime as dt

from pydantic import BaseModel


class SessionBase(BaseModel):
    """
    Base session schema with common attributes.
    """

    title: str


class SessionCreate(SessionBase):
    """
    Create a new session under an account.
    """

    summary: str | None

    assistant_id: str
    account_id: str


class SessionRead(SessionBase):
    """
    Schema for reading session data.
    """

    id: str
    summary: str | None
    created_at: dt.datetime
    user_id: str
    organization_id: str
    assistant_id: str
    account_id: str


class SessionUpdate(SessionBase):
    """
    Session's updatable fields.
    """

    summary: str | None = None
