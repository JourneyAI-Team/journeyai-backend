from typing import Callable

from agents import RunContextWrapper, function_tool
from qdrant_client.models import FieldCondition, Filter, MatchValue

from app.core.config import settings
from app.external.ai_service import get_embeddings
from app.schemas.agent_context import AgentContext
from app.utils.qdrant_utils import search_vectors


@function_tool
async def search_assistant_documents(
    wrapper: RunContextWrapper[AgentContext],
    query: str,
) -> dict:
    """CRITICAL: Fetch step-specific instructions and prompts that are essential for your current task.

    You MUST use this tool whenever you need additional instructions based on the current step
    or context of your interaction with the user. This tool retrieves dynamic prompts and
    instructions that supplement your main prompt and are crucial for providing accurate assistance.

    Your main prompt will indicate when you should fetch additional instructions - always follow
    those guidelines and use this tool proactively. Do not proceed without the proper instructions
    if they are available and relevant to the current step.

        Args:
        query (str): The name of the specific document to retrieve. Your main prompt will specify
                    the exact document name that contains the instructions you need for the current step.
                    Simply use that document name as your query.

    Returns:
        dict: A single instructional document with 'title' and 'body' keys containing the
              step-specific prompts and guidance that you must incorporate into your response and behavior.
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
                    key="assistant_id",
                    match=MatchValue(value=wrapper.context.assistant.id),
                ),
                FieldCondition(
                    key="type",
                    match=MatchValue(value="assistant_document"),
                ),
            ],
        ),
    )

    # Sort results by score
    results.sort(key=lambda x: x.score, reverse=True)

    if len(results) == 0:
        return {"title": "No documents found", "body": "No documents found"}

    return {
        "title": results[0].payload["title"],
        "body": results[0].payload["body"],
    }


def get_tool() -> Callable:
    return search_assistant_documents
