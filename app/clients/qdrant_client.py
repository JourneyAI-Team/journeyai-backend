# pylint: disable=E0611,W0406

from typing import List

from loguru import logger
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import PointStruct

from app.core.config import settings

_qdrant_async_client = None


def get_async_qdrant_client():
    global _qdrant_async_client
    _qdrant_async_client = AsyncQdrantClient(
        url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY
    )
    return _qdrant_async_client


async def insert_vector(
    collection_name: str, id: str, payload: dict[str, str], vector: List[float]
):
    client = get_async_qdrant_client()
    try:
        points_struct = PointStruct(id=id, payload=payload, vector=vector)
        await client.upsert(collection_name=collection_name, points=[points_struct])
    except Exception as e:
        logger.exception(f"Error inserting vector: {str(e)}")
        raise
