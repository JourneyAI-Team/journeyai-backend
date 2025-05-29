from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.api.deps import get_current_user
from app.models.account import Account
from app.models.assistant import Assistant
from app.models.session import Session
from app.models.user import User
from app.schemas.session import SessionCreate, SessionRead, SessionUpdate

router = APIRouter()


@router.post(
    "/",
    response_model=SessionRead,
    status_code=status.HTTP_201_CREATED,
    description="Create a new session under an account.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Account could not be found."},
    },
)
async def create_session(
    session: SessionCreate,
    current_user: User = Depends(get_current_user),
):

    with logger.contextualize(
        user_id=current_user.id, organization_id=current_user.organization_id
    ):
        logger.info(f"Create session request received. {session.title=}")

        # Check if the account exists
        account = await Account.find_one(
            Account.organization_id == current_user.organization_id,
            Account.id == session.account_id,
        )
        if not account:
            logger.warning("Account could not be found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account could not be found.",
            )

        # Check if the assistant exists
        assistant = await Assistant.find_one(Assistant.id == session.assistant_id)
        if not assistant:
            logger.warning("Assistant could not be found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assistant could not be found.",
            )

        # Create the new session
        new_session = Session(
            title=session.title,
            summary=session.summary,
            account_id=account.id,
            assistant_id=session.assistant_id,
            user_id=current_user.id,
            organization_id=current_user.organization_id,
        )

        try:
            # Save the new session to the database
            await new_session.insert()
            logger.success(f"Session created successfully. {new_session.title=}")
        except Exception as e:
            logger.exception(
                f"Database insert failed when creating session. {new_session.title=}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating session.",
            )
        return new_session


@router.get(
    "/{session_id}",
    response_model=SessionRead,
    description="Retrieve a session under an account by its id.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Session could not be found."},
    },
)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
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


@router.patch(
    "/{session_id}",
    response_model=SessionRead,
    description="Update a session's title and/or summary.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Session could not be found."},
    },
)
async def update_session(
    session_id: str,
    session_in: SessionUpdate,
    current_user: User = Depends(get_current_user),
):
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

        try:
            update_data = session_in.model_dump(exclude_unset=True)
            await session.set(update_data)
            logger.success("Session updated successfully.")
        except Exception as e:
            logger.exception(
                f"Database update failed when updating session. {session_in.title=}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating session.",
            )
        return session


@router.delete(
    "/{session_id}",
    description="Delete a session.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Session could not be found."},
    },
)
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
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
        try:
            await session.delete()
            logger.success("Session deleted successfully.")
        except Exception as e:
            logger.exception(
                f"Database delete failed when deleting session. {session_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting session.",
            )
