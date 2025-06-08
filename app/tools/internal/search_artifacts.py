from typing import Callable

from agents import RunContextWrapper, function_tool
from qdrant_client.models import FieldCondition, Filter, MatchValue

from app.core.config import settings
from app.external.ai_service import get_embeddings
from app.schemas.agent_context import AgentContext
from app.utils.qdrant_utils import search_vectors


@function_tool
async def search_artifacts(
    wrapper: RunContextWrapper[AgentContext],
    query: str,
) -> dict:
    """
    Args:
        query: The query string to use to search for artifacts.
    """

    search_embedding = await get_embeddings(query)
    results = await search_vectors(
        collection_name="Artifacts",
        query_embedding=search_embedding,
        top_k=10,
        score_threshold=settings.SEARCH_ARTIFACTS_SCORE_THRESHOLD,
        filter=Filter(
            must=[
                FieldCondition(
                    key="account_id", match=MatchValue(value=wrapper.context.account.id)
                )
            ]
        ),
    )

    # Sort results by score
    results.sort(key=lambda x: x.score, reverse=True)

    # Format results
    artifacts = []
    for result in results:
        artifacts.append(
            {
                "id": result.id,
                "title": result.payload["title"],
                "body": result.payload["body"],
                "type": result.payload["type"],
            }
        )

    return artifacts


def get_tool() -> Callable:
    return search_artifacts
