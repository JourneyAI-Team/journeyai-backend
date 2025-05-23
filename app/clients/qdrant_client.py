# pylint: disable=E0611,W0406

from typing import List

from loguru import logger
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import PointStruct

from app.core.config import settings


class QdrantClientSingleton:
    """
    Singleton class for managing an asynchronous Qdrant client.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            try:
                cls._instance = AsyncQdrantClient(
                    url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY
                )
                logger.success("Asynchronous Qdrant client initialized")
            except Exception as e:
                logger.exception(f"Error initializing Qdrant client: {str(e)}")
                raise
        return cls._instance


def get_async_qdrant_client():
    """
    Get an asynchronous Qdrant client instance.

    Returns
    -------
    AsyncQdrantClient
        An asynchronous Qdrant client instance.
    """
    return QdrantClientSingleton()


async def insert_vector(
    collection_name: str, id: str, payload: dict[str, str], vector: List[float]
):
    """
    Insert a vector into a Qdrant collection.

    Parameters
    ----------
    collection_name : str
        The name of the collection.
    id : str
        The ID of the vector.
    payload : dict[str, str]
        The payload associated with the vector.
    vector : List[float]
        The vector to insert.

    Raises
    ------
    Exception
        If there is an error inserting the vector.
    """

    client = get_async_qdrant_client()
    try:
        points_struct = PointStruct(id=id, payload=payload, vector=vector)
        await client.upsert(collection_name=collection_name, points=[points_struct])
    except Exception as e:
        logger.exception(f"Error inserting vector: {str(e)}")
        raise
