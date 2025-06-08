from loguru import logger
from qdrant_client.models import Filter, PointStruct, ScoredPoint

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


async def search_vectors(
    collection_name: str,
    query_embedding: list[float],
    top_k: int,
    filter: Filter | None = None,
    score_threshold: float | None = None,
) -> list[ScoredPoint]:
    """
    Search for vectors in a Qdrant collection.

    Parameters
    ----------
    collection_name : str
        The name of the collection to search in.
    query_embedding : list[float]
        The query vector to search for.
    top_k : int
        The number of top results to return.
    filter : Filter | None
        The filter to apply to the search.
    score_threshold : float | None
        The score threshold to apply to the search.

    Returns
    -------
    list
        A list of search results.
    """

    client = get_async_qdrant_client()
    try:
        response = await client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=top_k,
            query_filter=filter,
            score_threshold=score_threshold,
        )
        return response
    except Exception as e:
        logger.exception(f"Error searching vectors: {str(e)}")
        raise
