from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.api.deps import get_current_user
from app.models.account import Account
from app.models.message import Message
from app.models.session import Session
from app.models.user import User
from app.schemas.message import MessageRead

router = APIRouter()


@router.get(
    "/",
    response_model=list[MessageRead],
    description="List messages in a session under an account, sorted from oldest to latest.",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Account or session could not be found."
        },
    },
)
async def list_messages(
    account_id: str,
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all messages for a given session in a given account.

    Parameters
    ----------
    account_id : str
        The ID of the account containing the session.
    session_id : str
        The ID of the session to retrieve messages from.
    current_user : User
        The authenticated user making the request.

    Returns
    -------
    list[MessageRead]
        List of messages sorted from oldest to latest, limited to 150 messages.

    Raises
    ------
    HTTPException
        404 if the account or session could not be found.
    """
    with logger.contextualize(
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        account_id=account_id,
        session_id=session_id,
    ):
        logger.info("List messages request received.")

        # Check if account exists and belongs to the user's organization
        account = await Account.find_one(
            Account.id == account_id,
            Account.organization_id == current_user.organization_id,
        )

        if not account:
            logger.warning("Account could not be found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account could not be found.",
            )

        # Check if session exists and belongs to the account
        session = await Session.find_one(
            Session.id == session_id,
            Session.account_id == account_id,
            Session.organization_id == current_user.organization_id,
        )

        if not session:
            logger.warning("Session could not be found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session could not be found.",
            )

        # Retrieve messages for the session, sorted from oldest to latest, limited to 150
        messages = (
            await Message.find(
                Message.session_id == session_id,
                Message.account_id == account_id,
                Message.organization_id == current_user.organization_id,
            )
            .sort("created_at")  # Sort from oldest to latest
            .limit(150)  # Limit to 150 messages
            .to_list()
        )

        logger.success(f"Found {len(messages)} messages for session.")
        return messages
