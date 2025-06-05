from loguru import logger
from qdrant_client import models
from qdrant_client.http.exceptions import UnexpectedResponse

from app.clients.qdrant_client import get_async_qdrant_client


async def create_collection_if_not_exists(collection_name: str):
    """
    Create a Qdrant collection with specified name and vector configuration if it does not already exist.

    Parameters
    ----------
    collection_name : str
        The name of the collection to create.

    Raises
    ------
    UnexpectedResponse
        If there is an error creating the collection.
    """

    client = get_async_qdrant_client()

    if not await client.collection_exists(collection_name):
        try:
            await client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=1536, distance=models.Distance.COSINE
                ),
            )
        except UnexpectedResponse as e:
            if e.status_code == 409:
                logger.warning(f"Collection '{collection_name}' already exists")
            else:
                raise e


async def init_qdrant_db():
    """
    Initialize qdrant collections
    """

    await create_collection_if_not_exists("Artifacts")
    await create_collection_if_not_exists("Messages")
