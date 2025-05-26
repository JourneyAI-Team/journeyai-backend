from typing import List

from agents import Agent, Runner
from loguru import logger
from openai.types.responses.response_input_item_param import ResponseInputItemParam

from app.clients.openai_client import get_openai_async_client


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


async def generate_response(agent: Agent, input: list[ResponseInputItemParam]):
    """
    Generate a response using the specified agent and input.

    Parameters
    ----------
    agent : Agent
        The agent instance used to generate the response.
    input : list[ResponseInputItemParam]
        A list of input parameters for the response generation.

    Yields
    ------
    event
        An event from the result stream of the response generation process.
    """

    logger.info(f"Generating response using agent: {agent.name}")
    result = Runner.run_streamed(agent, input=input)

    async for event in result.stream_events():
        yield event
