from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.api.deps import get_current_user
from app.clients.arq_client import get_arq
from app.models.account import Account
from app.models.artifact import Artifact
from app.models.session import Session
from app.models.user import User
from app.schemas.artifact import ArtifactCreate, ArtifactRead, ArtifactUpdate

router = APIRouter()


@router.post(
    "/",
    response_model=ArtifactRead,
    status_code=status.HTTP_201_CREATED,
    description="Create an artifact.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Session does not exist."},
        status.HTTP_400_BAD_REQUEST: {
            "description": "Session id is required if account id is not provided."
        },
    },
)
async def create_artifact(
    artifact: ArtifactCreate, current_user: User = Depends(get_current_user)
):

    arq = await get_arq()

    with logger.contextualize(
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        session_id=artifact.session_id,
        account_id=artifact.account_id,
    ):
        logger.info(f"Create artifact request received. {artifact.title}")

        account_id = None
        if artifact.account_id:
            account_id = artifact.account_id
        else:

            if artifact.session_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Session id is required if account id is not provided.",
                )

            session = await Session.find_one(
                Session.id == artifact.session_id,
                Session.organization_id == current_user.organization_id,
            )
            if not session:
                logger.warning("Session does not exist.")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session does not exist.",
                )

            account_id = session.account_id

        new_artifact = Artifact(
            title=artifact.title,
            type=artifact.type,
            origin_type=artifact.origin_type,
            body=artifact.body,
            is_parent=artifact.is_parent,
            parent_id=artifact.parent_id,
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            session_id=artifact.session_id,
            account_id=account_id,
        )

        try:
            await new_artifact.insert()
            await arq.enqueue_job(
                "post_artifact_creation",
                new_artifact.id,
                _queue_name="artifacts",
            )

            logger.success(f"Artifact created successfully. {artifact.title=}")
        except Exception as e:
            logger.exception(
                f"Database insert failed when creating artifact. {artifact.title=}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating artifact.",
            ) from e
    return new_artifact


@router.get(
    "/",
    response_model=list[ArtifactRead],
    status_code=status.HTTP_200_OK,
    description="List artifacts.",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Account does not exist or is not accessible."
        },
    },
)
async def list_artifacts(
    account_id: str,
    opportunity_id: str | None = None,
    contact_id: str | None = None,
    current_user: User = Depends(get_current_user),
):
    with logger.contextualize(
        user_id=current_user.id, organization_id=current_user.organization_id
    ):
        logger.info("List artifacts request received.")

        # Check if the account exists and is accessible by the current user
        account = await Account.find_one(
            Account.id == account_id,
            Account.organization_id == current_user.organization_id,
        )
        if not account:
            logger.warning(
                f"Account does not exist or is not accessible. {account_id=}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account does not exist or is not accessible.",
            )

        query = {}
        if opportunity_id:
            query["opportunity_id"] = opportunity_id
        if contact_id:
            query["contact_id"] = contact_id

        artifacts = await Artifact.find(
            Artifact.account_id == account_id,
            Artifact.organization_id == current_user.organization_id,
            query,
        ).to_list()

        logger.info(f"Found {len(artifacts)} artifacts.")

        return artifacts


@router.patch(
    "/{artifact_id}",
    response_model=ArtifactRead,
    status_code=status.HTTP_200_OK,
    description="Update an artifact.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Artifact does not exist."},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Error updating artifact."
        },
    },
)
async def update_artifact(
    artifact_id: str,
    artifact_in: ArtifactUpdate,
    current_user: User = Depends(get_current_user),
):

    with logger.contextualize(
        user_id=current_user.id, organization_id=current_user.organization_id
    ):
        logger.info(f"Update artifact request received. {artifact_in=}")

        # Check if artifact exists
        artifact = await Artifact.find_one(
            Artifact.id == artifact_id,
            Artifact.organization_id == current_user.organization_id,
        )
        if not artifact:
            logger.warning(f"Artifact does not exist. {artifact_id=}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Artifact does not exist.",
            )

        try:
            # Update the artifact
            await artifact.set(artifact_in)
            logger.success("Artifact updated successfully.")
        except Exception as e:
            logger.exception(
                f"Database update failed when updating artifact. {artifact.id=}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating artifact.",
            ) from e
    return artifact


@router.delete(
    "/{artifact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete an artifact.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Artifact could not be found."},
    },
)
async def delete_artifact(
    artifact_id: str,
    current_user: User = Depends(get_current_user),
):
    with logger.contextualize(
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        artifact_id=artifact_id,
    ):
        logger.info("Delete artifact request received.")
        artifact = await Artifact.find_one(
            Artifact.id == artifact_id,
            Artifact.organization_id == current_user.organization_id,
        )
        if not artifact:
            logger.warning(f"Artifact could not be found. {artifact_id= }")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Artifact could not be found.",
            )
        try:
            # Delete the artifact
            await artifact.delete()
            logger.success("Session deleted successfully.")
        except Exception as e:
            logger.exception(
                f"Database delete failed when deleting artifact. {artifact.id=}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting artifact.",
            ) from e
