import pprint
from typing import List

from agents import Agent, RunConfig, Runner
from loguru import logger
from openai.types.responses.response_input_item_param import ResponseInputItemParam

from app.clients.groq_client import get_groq_async_client
from app.clients.openai_client import get_openai_async_client
from app.core.config import settings
from app.models.account import Account
from app.models.assistant import Assistant
from app.models.message import Message
from app.models.organization import Organization
from app.models.session import Session
from app.models.user import User
from app.schemas.agent_context import AgentContext
from app.schemas.types import SenderType


async def create_summary_for_search(messages: list[Message]) -> str:
    """
    Summarize the list of provided messages.

    Parameters
    ----------
    messages : list[Message]
        The list of messages to summarize.

    Returns
    -------
    summary : str
        The summary of the list of messages.
    """

    # Pre-processes the messages so that they are not too big
    messages = [x.model_dump() for x in messages]
    raw_messages = []
    for message in messages:

        data = {"sender": message.sender.value}

        if data["sender"] == SenderType.USER.value:
            data["content"] = (
                message.input["content"][:150] + "..."
                if len(message.input["content"]) > 150
                else message.input["content"]
            )
        else:
            if message.output:
                data["content"] = message.output
                data["content"].pop("id", None)
                data["content"].pop("annotations", None)

                # Remove file search results to not waste tokens
                if data["content"].get("type") == "file_search_call":
                    data["content"].pop("results", None)

        raw_messages.append(data)

    messages_input = pprint.pformat(messages)
    llm_input = [
        {
            "role": "user",
            "content": "You are an LLM agent that receives a large conversation dump in JSON format. Your task is to analyze the conversation and generate a concise search query string that represents the main topics, ideas, and keywords discussed in the conversation. The search query should be optimized for finding similar conversations using embeddings, and should include key topics, important entities, and core questions or themes from the discussion. Do not summarize the conversation—focus on extracting a relevant and precise search query.",
        },
        {
            "role": "user",
            "content": messages_input,
        },
    ]

    logger.debug(f"Creating summary for search for {len(messages)} messages.")

    if settings.GROQ_API_KEY:
        client = get_groq_async_client()

        chat_completion = await client.chat.completions.create(
            model="llama3-8b-8192",
            messages=llm_input,
        )

        summary = chat_completion.choices[0].message.content

    elif settings.OPENAI_API_KEY:
        client = get_openai_async_client()

        response = await client.responses.create(
            input=llm_input, model="chatgpt-4o-latest"
        )

        summary = response.output_text

    else:
        raise ValueError("No LLM provider configured. Cannot use any LLM service.")

    logger.info(f"Created summary for search for {len(messages)} messages.")

    return summary


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

    if not settings.OPENAI_API_KEY:
        raise ValueError("No OpenAI API key provided. Cannot use embedding service.")

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


async def generate_response(
    agent: Agent,
    input: list[ResponseInputItemParam],
    user_id: str,
    organization_id: str,
    account_id: str,
    session_id: str,
    assistant: Assistant,
    history: list[Message],
):
    """
    Generate a response using the specified agent and input.

    Parameters
    ----------
    agent : Agent
        The agent instance used to generate the response.
    input : list[ResponseInputItemParam]
        A list of input parameters for the response generation.
    user_id : str
        The user ID associated with the response.
    organization_id : str
        The organization ID associated with the response.
    account_id : str
        The account ID associated with the response.
    session_id : str
        The session ID associated with the response.
    history : list[Message]
        The history of messages associated with the response.

    Returns
    -------
    RunResultStreaming
        The result of the response generation process.
    """

    if not settings.OPENAI_API_KEY:
        raise ValueError("No OpenAI API key provided. Cannot use any LLM service.")

    user = await User.get(user_id)
    organization = await Organization.get(organization_id)
    account = await Account.get(account_id)
    session = await Session.get(session_id)

    agent_context = AgentContext(
        user=user,
        organization=organization,
        account=account,
        session=session,
        history=history,
        assistant=assistant,
    )

    logger.info(f"Generating response using agent: {agent.name}")
    result = Runner.run_streamed(
        agent,
        input=input,
        context=agent_context,
        run_config=RunConfig(
            group_id=session_id,
            trace_id=f"trace_{history[-1].id}",
            trace_metadata={
                "session_id": session_id,
                "assistant_id": assistant.id,
                "user_id": user_id,
                "organization_id": organization_id,
                "account_id": account_id,
            },
            workflow_name=agent.name,
        ),
    )

    return result
