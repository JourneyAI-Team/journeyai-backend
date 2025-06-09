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
    """Access your saved research findings and client knowledge base for better assistance.

    Use this tool to retrieve previously saved research artifacts, insights, and context that can
    inform your current analysis. This includes both research you've previously saved and
    user-provided information about clients, projects, and strategic context.

    **WHEN TO USE THIS TOOL:**
    - At the start of conversations to gather existing knowledge about a client or company
    - When you need background context before beginning new research
    - When looking for previous research findings about competitors or industry insights
    - When searching for stakeholder information or decision-maker profiles you've saved before
    - When building on previous analysis or connecting insights across conversations
    - When you need user preferences, goals, or strategic context for better assistance

    **RESEARCH-SPECIFIC USAGE:**
    - Find existing company profiles and competitive analyses
    - Retrieve previous stakeholder research and contact information
    - Access saved industry insights and market analysis
    - Locate customer profile research and target market findings
    - Search for meeting notes and strategic recommendations

    Think of this as accessing your research knowledge base to provide informed,
    context-aware assistance that builds on previous work.

    Args:
        query (str): Search terms describing what you're looking for (e.g., "company background",
            "competitive analysis", "stakeholder research", "industry trends", "previous insights")

    Returns:
        dict: List of matching research artifacts with details including title, body, and type
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
