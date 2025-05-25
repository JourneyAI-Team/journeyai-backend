from loguru import logger

from app.external.ai_service import get_embeddings
from app.models.artifact import Artifact
from app.utils.constructor_utils import construct_embedding_input_for_artifact
from app.utils.qdrant_utils import insert_vector


async def post_artifact_creation(ctx, id: str):
    artifact = await Artifact.get(id)

    logger.debug(f"Fetched artifact: {artifact.title}")

    # Generate embeddings from artifact
    embedding_input = construct_embedding_input_for_artifact(
        title=artifact.title, body=artifact.body, source="user"
    )

    artifact_embeddings = await get_embeddings(embedding_input)

    # Save embeddings to Qdrant
    await insert_vector(
        collection_name="Artifacts",
        id=artifact.id,
        payload={
            "session_id": artifact.session_id,
            "user_id": artifact.user_id,
            "organization_id": artifact.organization_id,
            "account_id": artifact.account_id,
        },
        vector=artifact_embeddings,
    )

    logger.success(f"Successfully embedded artifact: {artifact.title}")
