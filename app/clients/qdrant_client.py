from typing import List
import qdrant_client

from qdrant_client.conversions.common_types import Points
from loguru import logger
import qdrant_client.models
from app.core.config import settings

_qdrant_async_client = None


def get_async_qdrant_client():
    global _qdrant_async_client
    _qdrant_async_client = qdrant_client.AsyncQdrantClient(url=settings.QDRANT_URL)
    return _qdrant_async_client


async def insert_vector(
    collection_name: str, id: str, payload: dict[str, str], vector: List[float]
):
    client = get_async_qdrant_client()
    try:
        points_struct = qdrant_client.models.PointStruct(
            id=id, payload=payload, vector=vector
        )
        await client.upsert(collection_name=collection_name, points=[points_struct])
    except Exception as e:
        logger.exception(f"Error inserting vector: {str(e)}")
        raise
