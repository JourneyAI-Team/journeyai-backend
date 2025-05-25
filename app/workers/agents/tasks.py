from loguru import logger

from app.models.session import Session


async def process_session(ctx, connection_id: str, session_id: str):
    session = await Session.get(session_id)

    if not session:
        logger.error(f"Session not found: {session_id}")
        return

    logger.info(f"Processing session: {session_id}")
