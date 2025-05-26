from loguru import logger

from app.models.assistant import Assistant
from app.models.session import Session
from app.utils.assistant_utils import get_agent_from_assistant
from app.utils.websocket.communications import send_to_websocket


async def process_session(ctx, connection_id: str, session_id: str):

    await send_to_websocket(
        connection_id, "processing_session", {"session_id": session_id}
    )

    session = await Session.get(session_id)
    if not session:
        logger.error(f"Session not found: {session_id}")
        return

    assistant = await Assistant.get(session.assistant_id)
    if not assistant:
        logger.error(f"Assistant not found: {session.assistant_id}")
        return

    agent = get_agent_from_assistant(assistant)

    logger.info(f"Processing session: {session_id}")
