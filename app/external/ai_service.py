from typing import List

from app.utils.openai_client import get_openai_async_client


async def get_embeddings(embedding_input: str, source: str) -> List[float]:
    client = get_openai_async_client()
    if source == "user":
        embedding_input = (
            f"""
        Uploaded By User
        """
            + embedding_input
        )

    response = await client.embeddings.create(
        input=embedding_input, model="text-embedding-3-small"
    )
    return response.data[0].embedding
