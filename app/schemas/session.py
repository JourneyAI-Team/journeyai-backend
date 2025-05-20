from pydantic import BaseModel


class SessionBase(BaseModel):
    """
    Base session schema with common attributes.
    """

    title: str


class SessionCreate(SessionBase):
    """
    Create a new session under an account.

    Parameters
    -----
    title : str, optional
            Session title
    summary : str, optional
            Session summary
    assistant_id : str
            The id of the Assistant for this session
    account_id : str
            Account this session is tied to.
    """

    title: str | None
    summary: str | None
    assistant_id: str
    account_id: str


class SessionRead(SessionBase):
    """
    Schema for reading session data.

    Parameters
    -----
    title : str
            Session title
    summary : str, optional
            Session summary
    assistant_id : str
            The id of the Assistant for this session
    account_id : str
            Account this session is tied to.
    user_id : str
            The id of the user who created this session.
    organization_id : str
            The id of the organization in which this session belongs to.
    """

    id: str
    title: str
    summary: str | None
    assistant_id: str
    account_id: str
    user_id: str
    organization_id: str


class SessionUpdate(SessionBase):
    """
    Session's updateable fields.

    Parameters
    -----
    title : str
            Session title
    summary : str, optional
            Session summary

    """

    title: str
    summary: str | None
