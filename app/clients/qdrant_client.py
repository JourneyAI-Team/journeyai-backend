# pylint: disable=E0611,W0406

from loguru import logger
from qdrant_client import AsyncQdrantClient

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
