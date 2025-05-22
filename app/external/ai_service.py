from typing import List

from loguru import logger

from app.schemas.types import EmbeddingInputSourceType
from app.utils.openai_client import get_openai_async_client


async def get_embeddings(embedding_input: str) -> List[float]:
    """
    Transform text to vector embeddings.
    Prepend "Uploaded by user" to text if source text is from user.

    Parameters
    -----
    embedding_input : str
        The string text to embed.

    source : str
        Text source.

    Returns
    -----
    embeddings : list(float)
        Returns the vector embeddings result which is a list of floating point numbers of size 1536.
    """
    client = get_openai_async_client()
    try:
        response = await client.embeddings.create(
            input=embedding_input, model="text-embedding-3-small"
        )
        return response.data[0].embedding
    except Exception as e:
        logger.exception(
            f"Failed to transform text to vector embeddings. {embedding_input=}"
        )
        raise
