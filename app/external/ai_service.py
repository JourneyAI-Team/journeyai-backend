from typing import List

from agents import Agent, Runner
from loguru import logger
from openai.types.responses.response_input_item_param import ResponseInputItemParam

from app.clients.groq_client import get_groq_async_client
from app.clients.openai_client import get_openai_async_client
from app.core.config import settings
from app.models.account import Account
from app.models.message import Message
from app.models.organization import Organization
from app.models.session import Session
from app.models.user import User
from app.schemas.agent_context import AgentContext


async def create_summary(messages: list[Message]) -> str:
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

    if settings.GROQ_API_KEY:
        client = get_groq_async_client()
    elif settings.OPENAI_API_KEY:
        client = get_openai_async_client()
    else:
        raise ValueError("No LLM provider configured. Cannot use any LLM service.")


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


async def generate_response(
    agent: Agent,
    input: list[ResponseInputItemParam],
    user_id: str,
    organization_id: str,
    account_id: str,
    session_id: str,
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

    Yields
    ------
    event
        An event from the result stream of the response generation process.
    """

    user = await User.get(user_id)
    organization = await Organization.get(organization_id)
    account = await Account.get(account_id)
    session = await Session.get(session_id)

    agent_context = AgentContext(
        user=user, organization=organization, account=account, session=session
    )

    logger.info(f"Generating response using agent: {agent.name}")
    result = Runner.run_streamed(agent, input=input, context=agent_context)

    return result
