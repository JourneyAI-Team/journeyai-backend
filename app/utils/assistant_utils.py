import json
import pprint

from agents import Agent, RunContextWrapper, WebSearchTool
from loguru import logger
from qdrant_client.models import FieldCondition, Filter, MatchValue

from app.external.ai_service import create_summary_for_search, get_embeddings
from app.models.account import Account
from app.models.assistant import Assistant
from app.models.message import Message
from app.models.organization import Organization
from app.models.session import Session
from app.models.user import Profile, User
from app.schemas.agent_context import AgentContext
from app.schemas.types import SenderType
from app.utils.qdrant_utils import search_vectors
from app.utils.tool_utils import get_tool


async def generate_instruction_context(
    messages: list[Message],
    user: User,
    organization: Organization,
    account: Account,
    session: Session,
    assistant: Assistant,
) -> dict:
    """
    Generate context that will be passed onto the LLM. Context includes:
    - Artifacts related to the current conversation.
    - Messages (either from this or another session) that may or may not be related to the current conversation.
    - User profile information for personalization.
    """

    with logger.contextualize(
        user_id=user.id,
        organization_id=organization.id,
        account_id=account.id,
        session_id=session.id,
        assistant_id=assistant.id,
        message_id=messages[-1].id,
    ):

        logger.debug("Generating instructions context...")
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
                        match=MatchValue(value=account.id),
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

        # Fetch related messages
        related_messages = await search_vectors(
            collection_name="Messages",
            query_embedding=search_query_embedding,
            top_k=20,
            filter=Filter(
                must=[
                    FieldCondition(
                        key="account_id", match=MatchValue(value=account.id)
                    ),
                ]
            ),
        )
        related_messages_content = parse_related_messages(related_messages)
        logger.debug(f"Related messages: {pprint.pformat(related_messages_content)}")

        # Parse user profile information
        user_profile = parse_user_profile(user.profile)
        logger.debug(f"User profile: {pprint.pformat(user_profile)}")

        logger.info("Generated instructions context.")
        return {
            "artifacts": related_artifacts_content,
            "messages": related_messages_content,
            "user_profile": user_profile,
        }


async def create_instructions(
    wrapper: RunContextWrapper[AgentContext], agent: Agent[AgentContext]
) -> str:

    assistant = wrapper.context.assistant

    instructions_context = await generate_instruction_context(
        wrapper.context.history,
        wrapper.context.user,
        wrapper.context.organization,
        wrapper.context.account,
        wrapper.context.session,
        wrapper.context.assistant,
    )

    instructions = (
        assistant.developer_prompt
        + "\n\n"
        + f"""## Additional Context
Below is additional context that you will be utilizing in order to give out the best responses and make the best decisions possible. Provided are artifacts and messages that may be related to the current conversation, as well as user profile information for personalization.

### User Profile
Use the user profile information to personalize your responses, understand the user's context, preferences, and communication style. This information can help you:
- Tailor your communication style to match the user's preferences
- Reference their interests, goals, and background when relevant
- Provide more relevant and contextual assistance
- Build rapport and maintain continuity in conversations

### Account Information
Some basic information about the account you are working under:
- Name: {wrapper.context.account.name}
- Description: {wrapper.context.account.description}

### Context Data
```json
{json.dumps(instructions_context, indent=2)}
```
"""
    )

    logger.debug(f"Instructions: {instructions}")
    logger.info("Created instructions.")

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


def parse_related_messages(messages: list[dict]) -> list[dict]:
    """
    Parse the related messages into a list of dictionaries.
    """

    related_messages = []
    for message in messages:
        data = {
            "id": message.id,
            "sender": message.payload["sender"],
        }

        if data["sender"] == SenderType.USER.value:
            data["content"] = message.payload["input"]["content"]
        else:
            data["content"] = message.payload["output"]

        related_messages.append(data)

    return related_messages


def parse_user_profile(profile: Profile) -> dict:
    """
    Parse user profile information into a clean dictionary format.
    Only includes fields that have values to avoid cluttering the context.

    Parameters
    ----------
    profile : Profile
        User profile object

    Returns
    -------
    dict
        Clean dictionary containing only populated profile fields
    """

    # Convert profile to dict and filter out None/empty values
    profile_dict = (
        profile.model_dump() if hasattr(profile, "model_dump") else profile.__dict__
    )
    return {
        k: v for k, v in profile_dict.items() if v is not None and v != [] and v != {}
    }
