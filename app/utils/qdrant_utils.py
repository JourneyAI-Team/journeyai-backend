from loguru import logger
from qdrant_client.models import PointStruct

from app.clients.qdrant_client import get_async_qdrant_client


async def insert_vector(
    collection_name: str, id: str, payload: dict[str, str], vector: list[float]
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
    vector : list[float]
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
