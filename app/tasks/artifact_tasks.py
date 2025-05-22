import os
import asyncio

from app.tasks.worker import celery_app
from app.external.ai_service import get_embeddings

from app.utils.constructor_utils import construct_embedding_input_for_artifact
from app.utils.qdrant_client import insert_vector

from app.models.artifact import Artifact


def post_artifact_creation():
    print("HELLOOOOOO")
    # # Generate embeddings from artifact
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
    return "hello world"
