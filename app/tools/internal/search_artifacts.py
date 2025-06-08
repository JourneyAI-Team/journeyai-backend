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
    """Access stored information and context to provide better assistance.

    Use this tool to retrieve stored artifacts containing various types of information that can inform your responses.
    Artifacts include both assistant-saved memories and user-provided context such as documents, lead information,
    project details, and other relevant data.

    Consider searching for artifacts proactively, especially at the start of conversations or when context is lacking:
    - Look for user preferences, goals, and background information
    - Find user-provided documents or context about specific leads/projects
    - Retrieve past insights or discoveries relevant to current topics
    - Access historical context that builds understanding over time
    - Find any information that would help provide better assistance

    Think of this as accessing a shared knowledge base to understand the full context and provide more
    informed, personalized responses.

    Args:
        query: The query string to use to search for artifacts. Use descriptive terms related to
            what you're looking for (e.g., "user preferences", "project goals", "previous insights").
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
                ),
            ],
            must_not=[
                FieldCondition(
                    key="type",
                    match=MatchValue(value="assistant_document"),
                ),
            ],
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
