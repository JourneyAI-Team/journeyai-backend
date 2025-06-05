from loguru import logger

from app.external.ai_service import get_embeddings
from app.models.message import Message
from app.utils.constructor_utils import construct_embedding_input_for_message
from app.utils.qdrant_utils import insert_vector


async def post_message_creation(ctx, id: str):

    message = await Message.get(id)
    logger.debug(f"Fetched message: {id}")

    embedding_input = await construct_embedding_input_for_message(message)
    message_embeddings = await get_embeddings(embedding_input)

    await insert_vector(
        collection_name="Messages",
        id=message.id,
        payload=message.model_dump(),
        vector=message_embeddings,
    )

    logger.success(f"Successfully embedded message: {message.id}")
