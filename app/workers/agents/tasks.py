from loguru import logger

from app.models.session import Session
from app.utils.websocket.communications import send_to_websocket


async def process_session(ctx, connection_id: str, session_id: str):

    await send_to_websocket(
        connection_id, "processing_session", {"session_id": session_id}
    )

    session = await Session.get(session_id)

    if not session:
        logger.error(f"Session not found: {session_id}")
        return

    logger.info(f"Processing session: {session_id}")
