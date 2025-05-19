from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.api.deps import get_current_user
from app.models.account import Account
from app.models.assistant import Assistant
from app.models.session import Session
from app.models.user import User
from app.schemas.session import SessionCreate, SessionRead, SessionUpdate

router = APIRouter()


@router.post("/", response_model=SessionRead)
async def create_session(
    session: SessionCreate,
    current_user: User = Depends(get_current_user),
):
    """
    Create a new session under an account.
    Can create multiple sessions under an account.

    Parameters
    -----
        session : SessionCreate
            Request body. Fields required to create a new session.

    Returns
    -----
        SessionRead
            Returns the newly created session information.

    Raises
    -----
    HTTPException
        404 if account or assistant could not be found.
    """
    with logger.contextualize(
        user_id=current_user.id, organization_id=current_user.organization_id
    ):
        logger.info(f"Create session request received. {session.title=}")

        # Check if the account exists
        account = await Account.find_one(Account.id == session.account_id)
        if not account:
            logger.warning("Account could not be found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account could not be found.",
            )

        # Check if the assistant exists
        # NOTE: Temporarily commented out this check since there's no way to save and retrieve assistants yet
        # assistant = await Assistant.find_one(
        #     Assistant.id == session.assistant_id
        # )
        # if not assistant:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail="Assistant could not be found."
        #     )

        # Create the new session
        new_session = Session(
            title=session.title,
            summary=session.summary,
            account_id=account.id,
            # NOTE: Change to an actual assistant's id (assistant.id)
            assistant_id="temporary_assistant_id",
            user_id=current_user.id,
            organization_id=current_user.organization_id,
        )

        # Save the new session to the database
        await new_session.insert()
        logger.success(f"Session created successfully. {new_session.title=}")

        return new_session


@router.get("/{session_id}", response_model=SessionRead)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get a session under an account by its id.

    Parameters
    -----
    session_id : str
        Path parameter. The session id to retrieve.

    Returns
    -----
    SessionRead
        The session information.

    Raises
    -----
    HTTPException
        404 if session could not be found.
    """
    with logger.contextualize(
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        session_id=session_id,
    ):
        logger.info("Retrieve session request received.")

        # Check if session exists
        session = await Session.find_one(
            Session.id == session_id,
            Session.organization_id == current_user.organization_id,
        )
        if not session:
            logger.warning("Session could not be found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session could not be found.",
            )
        logger.success("Session retrieved successfully.")
        return session


@router.patch("/{session_id}")
async def update_session(
    session_id: str,
    session_in: SessionUpdate,
    current_user: User = Depends(get_current_user),
):
    """
    Update a session's title and/or summary.

    Parameters
    -----
    session_id: str
        Path parameter. The session's id to update.
    session_in: SessionUpdate
        Request Body. Fields that can be updated.

    Returns
    -----
    dict
        Empty Dictionary

    Raises
    -----
    HTTPException
        404 if session could not be found.
    """
    with logger.contextualize(
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        session_id=session_id,
    ):
        logger.info(f"Update session request received. {session_in=}")

        # Check if session exists.
        session = await Session.find_one(
            Session.id == session_id,
            Session.organization_id == current_user.organization_id,
        )
        if not session:
            logger.warning("Session could not be found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session could not be found.",
            )

        # Update the account, only description is allowed to be updated
        await session.set(
            {Session.summary: session_in.summary, Session.title: session_in.title}
        )
        logger.success("Session updated successfully.")

        return {}


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Delete a session.

    Parameters
    -----
    session_id: str
        Path parameter. The session's id to delete.

    Returns
    -----
    dict
        Empty dictionary.

    Raises
    -----
    HTTPException
        404 if session could not be found.
    """
    with logger.contextualize(
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        session_id=session_id,
    ):
        logger.info("Delete session request received.")

        # Check if session exists.
        session = await Session.find_one(
            Session.id == session_id,
            Session.organization_id == current_user.organization_id,
        )
        if not session:
            logger.warning("Session could not be found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session could not be found.",
            )
        await session.delete()
        logger.success("Session deleted successfully.")
        return {}
