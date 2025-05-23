import time
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.api.deps import get_current_user
from app.models.artifact import Artifact
from app.models.session import Session
from app.models.user import User
from app.schemas.artifact import ArtifactCreate, ArtifactUpdate
from app.tasks.artifact_tasks import post_artifact_creation
from app.tasks.queues import artifacts_queue

router = APIRouter()


@router.post("/", response_model=Artifact)
async def create_artifact(
    artifact: ArtifactCreate, current_user: User = Depends(get_current_user)
):
    """
    Create a new artifact.

    Parameters
    -----
    artifact: ArtifactCreate
        Request body. Fields required to create an artifact.

    Returns
    -----
    new_artifact: Artifact
        Returns the newly created artifact.

    Raises
    -----
    404 if session tied to the artifact does not exist.
    500 if database insert fails.
    """

    with logger.contextualize(
        user_id=current_user.id, organization_id=current_user.organization_id
    ):
        logger.info(f"Create artifact request received. {artifact.title}")

        # Check if session exists in the user's organization
        session = await Session.find_one(
            Session.id == artifact.session_id,
            Session.organization_id == current_user.organization_id,
        )
        if not session:
            logger.warning("Session does not exist.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session does not exist."
            )

        new_artifact = Artifact(
            title=artifact.title,
            type=artifact.type,
            origin_type=artifact.origin_type,
            body=artifact.body,
            is_parent=artifact.is_parent,
            parent_id=artifact.parent_id,
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            session_id=session.id,
            account_id=session.account_id,
        )

        try:
            await new_artifact.insert()
            logger.success(f"Artifact created successfully. {artifact.title=}")
        except Exception as e:
            logger.exception(
                f"Database insert failed when creating artifact. {artifact.title=}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating artifact.",
            ) from e

        # Generate embeddings from artifact
        # embedding_input = construct_embedding_input_for_artifact(
        #     title=new_artifact.title, body=new_artifact.body, source="user"
        # )

        # artifact_embeddings = await get_embeddings(embedding_input, source="user")

        # # Save embeddings to Qdrant
        # await insert_vector(
        #     collection_name="Artifacts",
        #     id=new_artifact.id,
        #     payload={
        #         "session_id": new_artifact.session_id,
        #         "user_id": new_artifact.user_id,
        #         "organization_id": new_artifact.organization_id,
        #         "account_id": new_artifact.account_id,
        #     },
        #     vector=artifact_embeddings,
        # )
    return new_artifact


@router.get("/", response_model=List[Artifact])
async def list_artifacts(
    account_id: str,
    opportunity_id: str | None = None,
    contact_id: str | None = None,
    current_user: User = Depends(get_current_user),
):
    """
    Get the list of artifacts under an organization.

    Parameters
    -----
    account_id : str
        Path parameter. Which account to query the list of artifacts from.
    opportunity_id : str, optional
        Query parameter. Filter by opportunity.
    contact_id : str, optional
        Query parameter. Filter by contact.

    Returns
    -----
    artifacts : list(Artifact)
        List of artifact objects.
    """
    with logger.contextualize(
        user_id=current_user.id, organization_id=current_user.organization_id
    ):
        logger.info("List artifacts request received.")
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
    return artifacts


@router.patch("/{artifact_id}", response_model=Artifact)
async def update_artifact(
    artifact_id: str,
    artifact_in: ArtifactUpdate,
    current_user: User = Depends(get_current_user),
):
    """
    Update an artifact.
    Ensure that original values are passed for any fields that will not be updated.

    Parameters
    -----
    artifact_id : str
        Path parameter. The artifact id to update.
    artifact_in : ArtifactUpdate
        Request body. The artifact fields to update.

    Returns
    -----
    artifact : Artifact
        The artifact's newly updated information object.

    Raises
    -----
    404 if artifact could not be found.
    """
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


@router.delete("/{artifact_id}")
async def delete_artifact(
    artifact_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Delete an artifact.

    Parameters
    -----
    artifact_id : str
        Path parameter. The artifact id to delete.

    Returns
    -----
    dict
        Empty dictionary.

    Raises
    -----
    404 if artifact could not be found within the current authenticated user's organization.
    """
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
        # Delete the artifact
        await artifact.delete()
        logger.success("Session deleted successfully.")
    return {}
