from loguru import logger

from app.clients.arq_client import get_arq
from app.models.message import Message
from app.models.user import User
from app.schemas.message import InputMessageSchema
from app.schemas.types import SenderType
from app.utils.websocket.handlers import register_handler


@register_handler("ingest_message")
async def ingest_message(connection_id: str, user: User, data: InputMessageSchema):

    arq = await get_arq()

    with logger.contextualize(
        connection_id=connection_id,
        user_id=user.id,
        organization_id=user.organization_id,
        session_id=data["session_id"],
        assistant_id=data["assistant_id"],
        account_id=data["account_id"],
    ):
        logger.debug(f"Ingesting message: {data}")

        new_message = Message(
            input=data,
            sender=SenderType.USER,
            user_id=user.id,
            organization_id=user.organization_id,
            session_id=data["session_id"],
            assistant_id=data["assistant_id"],
            account_id=data["account_id"],
        )
        await new_message.insert()

        with logger.contextualize(message_id=new_message.id):
            logger.info("Message saved. Sending message to agents worker...")

            await arq.enqueue_job(
                "process_session",
                connection_id,
                new_message.session_id,
                _queue_name="agents",
            )
