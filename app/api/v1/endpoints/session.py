from fastapi import APIRouter, Depends, UploadFile, HTTPException, File, status
from loguru import logger

from app.api.deps import get_current_user
from app.utils.file_upload_utils import (
    insert_uploaded_session_file,
    batch_insert_uploaded_session_files,
)

from app.models.account import Account
from app.models.assistant import Assistant
from app.models.session import Session
from app.models.user import User
from app.schemas.session import SessionCreate, SessionRead, SessionUpdate
from app.clients.openai_client import get_openai_async_client

router = APIRouter()

openai = get_openai_async_client()


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
            # Create a new vector store for the session
            vector_store = await openai.vector_stores.create(
                name=f"session:{new_session.id}"
            )

            logger.debug(f"Created vector store with ID: {vector_store.id}")

        except Exception as e:
            logger.exception(
                f"Vector store creation failed when creating session. {new_session.title=}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating vector store.",
            ) from e

        try:
            # Add the vector store id to the session
            new_session.vector_store_id = vector_store.id

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
            ) from e

        return new_session


@router.get(
    "/",
    response_model=list[SessionRead],
    description="List sessions under an account.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Session could not be found."},
    },
)
async def list_sessions(
    account_id: str,
    current_user: User = Depends(get_current_user),
):
    with logger.contextualize(
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        account_id=account_id,
    ):
        logger.info("List sessions request received.")

        # Check if account exists
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

        # Check if session exists
        sessions = (
            await Session.find(
                Session.account_id == account.id,
                Session.organization_id == current_user.organization_id,
            )
            .sort("-created_at")
            .to_list()
        )

        logger.success(f"Found {len(sessions)} sessions.")
        return sessions


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
            ) from e
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
            ) from e


@router.post(
    "/{session_id}/file",
    # response_model=FileRead,
    description="Upload a file to a session.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Session could not be found."},
    },
)
async def upload_file(
    session_id: str,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
):
    with logger.contextualize(
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        session_id=session_id,
    ):
        logger.info(
            f"Upload file request received: filename: {file.filename}, content_type: {file.content_type}, size: {file.size}"
        )

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
            if not session.vector_store_id:
                logger.warning("Session does not have a vector store id.")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Session does not have a vector store id.",
                )

            # Upload the file to the openai file storage
            await insert_uploaded_session_file(
                file,
                session.vector_store_id,
            )
            logger.success(f"File uploaded successfully. {file.filename=}")
            return {
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(await file.read()),
            }
        except Exception as e:
            logger.exception(
                f"Database insert failed when uploading file to session. {session_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error uploading file to session.",
            ) from e


@router.post(
    "/{session_id}/files",
    description="Upload multiple files to a session.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Session could not be found."},
    },
)
async def upload_files(
    session_id: str,
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
):
    with logger.contextualize(
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        session_id=session_id,
    ):
        logger.info(f"Upload files request received: {len(files)} files")

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
            if not session.vector_store_id:
                logger.warning("Session does not have a vector store id.")
                logger.info("Creating vector store for session...")
                vector_store = await openai.vector_stores.create(
                    name=f"session:{session.id}"
                )
                session.vector_store_id = vector_store.id
                await session.save()
                if not session.vector_store_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Session does not have a vector store id.",
                    )

            # await batch_insert_uploaded_session_files(files, session.vector_store_id)
            logger.success(f"Files uploaded successfully. {len(files)} files")
        except Exception as e:
            logger.exception(
                f"Database insert failed when uploading files to session. {session_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error uploading files to session.",
            ) from e
