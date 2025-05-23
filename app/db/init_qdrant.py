from qdrant_client import models

from app.clients.qdrant_client import get_async_qdrant_client


async def init_qdrant_db():
    """
    Initialize qdrant collections
    """

    client = get_async_qdrant_client()
    if not await client.collection_exists("Artifacts"):
        await client.create_collection(
            collection_name="Artifacts",
            vectors_config=models.VectorParams(
                size=1536, distance=models.Distance.COSINE
            ),
        )
