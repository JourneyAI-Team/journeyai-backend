from loguru import logger

from app.clients.arq_client import get_arq
from app.exceptions.session import SessionNotFoundError
from app.models.message import Message
from app.models.session import Session
from app.models.user import User
from app.schemas.message import IngestMessageSchema
from app.schemas.types import SenderType
from app.utils.websocket.handlers import register_handler


@register_handler("ingest_message")
async def ingest_message(connection_id: str, user: User, data: IngestMessageSchema):

    arq = await get_arq()

    session = await Session.get(data["session_id"])
    if session is None:
        raise SessionNotFoundError(f"Session not found for ID: {data['session_id']}")

    with logger.contextualize(
        connection_id=connection_id,
        user_id=user.id,
        organization_id=user.organization_id,
        session_id=session.id,
        assistant_id=session.assistant_id,
        account_id=session.account_id,
    ):
        logger.debug(f"Ingesting message: {data}")

        # Extract attachments if present
        attachments = data.get("attachments", [])

        new_message = Message(
            input={"content": data["content"]},
            sender=SenderType.USER,
            attachments=attachments,
            user_id=user.id,
            organization_id=user.organization_id,
            session_id=session.id,
            assistant_id=session.assistant_id,
            account_id=session.account_id,
            embed_after_insert=True,
        )
        await new_message.insert()
        await arq.enqueue_job(
            "post_message_creation",
            new_message.id,
            _queue_name="messages",
        )

        with logger.contextualize(message_id=new_message.id):
            logger.info("Message saved. Sending message to agents worker...")

            await arq.enqueue_job(
                "process_session",
                connection_id,
                new_message.session_id,
                _queue_name="agents",
            )
