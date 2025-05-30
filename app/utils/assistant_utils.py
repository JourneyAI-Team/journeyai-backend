from agents import Agent, WebSearchTool
from loguru import logger

from app.external.ai_service import create_summary_for_search, get_embeddings
from app.models.assistant import Assistant
from app.models.message import Message
from app.schemas.agent_context import AgentContext
from app.utils.qdrant_utils import search_vectors
from app.utils.tool_utils import get_tool


async def generate_instruction_context(messages: list[Message]) -> dict:
    """
    Generate context that will be passed onto the LLM. Context includes:
    - Artifacts related to the current conversation.
    - Messages (either from this or another session) that may or may not be related to the current conversation.
    """

    logger.info("Generating instruction context")
    search_query = await create_summary_for_search(messages)
    logger.info(f"Search query: {search_query}")

    search_query_embedding = await get_embeddings(search_query)

    # Fetch related artifacts
    related_artifacts = await search_vectors(
        collection_name="Artifacts",
        query_embedding=search_query_embedding,
        top_k=10,
        filter=Filter(
            must=[
                FieldCondition(
                    key="account_id",
                    match=Match(value=messages[0].account_id),
                )
            ]
        ),
    )
    related_artifacts_content = [
        {
            "id": result.id,
            "title": result.payload["title"],
            "body": result.payload["body"],
        }
        for result in related_artifacts
    ]

    return {"artifacts": related_artifacts_content}


async def create_instructions(
    wrapper: RunContextWrapper[AgentContext], assistant: Assistant
) -> str:
    return assistant.developer_prompt


def get_agent_from_assistant(assistant: Assistant) -> Agent:

    # Retrieve tools
    tools = []
    for tool in assistant.tool_config["tools"]:
        match tool["name"]:
            case "openai_web_search":
                tools.append(WebSearchTool())
            case _:
                tools.append(get_tool(tool["name"], tool["type"]))

    return Agent[AgentContext](
        name=assistant.name,
        model=assistant.model,
        tools=tools,
        instructions=create_instructions,
    )
