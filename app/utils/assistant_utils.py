import json
import pprint

from agents import Agent, RunContextWrapper, WebSearchTool
from loguru import logger
from qdrant_client.models import FieldCondition, Filter, Match

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

    logger.debug(f"Related artifacts: {pprint.pformat(related_artifacts_content)}")

    return {"artifacts": related_artifacts_content}


async def create_instructions(
    wrapper: RunContextWrapper[AgentContext], agent: Agent[AgentContext]
) -> str:

    assistant = wrapper.context.assistant

    if len(wrapper.context.history) > 2:

        instructions_context = await generate_instruction_context(
            wrapper.context.history
        )

        instructions = (
            assistant.developer_prompt
            + "\n\n"
            + f"""Below is additional context that you will be utilizing in order to give out the best responses and decisions possible.

```json
{json.dumps(instructions_context, indent=2)}
```
"""
        )

    instructions = assistant.developer_prompt

    logger.debug(f"Instructions: {instructions}")

    return instructions


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
