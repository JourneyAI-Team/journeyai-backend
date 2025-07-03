from loguru import logger

from app.core.config import settings
from app.db.init_mongo import init_db
from app.db.init_qdrant import init_qdrant_db
from app.utils.loki_logger import setup_logger
from app.utils.prompt_utils import insert_preloaded_assistant
from app.utils.websocket.redis_listener import start_redis_listener


async def setup_loki_logger():
    """
    Set up the Loki logger.

    This function sets up the Loki logger if the LOKI_URL is configured.
    """

    if settings.LOKI_URL:
        setup_logger(
            settings.LOKI_URL,
            labels={"job": "journey", "environment": settings.ENVIRONMENT},
        )


async def initialize_app():
    """
    Initialize the main application.

    This function sets up the Loki logger, initializes the MongoDB and Qdrant
    databases, and starts the Redis listener for WebSocket messages.
    """
    await setup_loki_logger()

    logger.info("Initializing app...")

    logger.info("Initializing database...")
    await init_db()
    logger.success("Database initialized successfully")

    logger.info("Initializing Qdrant database...")
    await init_qdrant_db()
    logger.success("Qdrant database initialized successfully")

    logger.info("Starting Redis listener...")
    await start_redis_listener()
    logger.success("Redis listener started successfully")

    logger.info("Inserting preloaded assistants...")
    await insert_preloaded_assistant("new_client_research_prep")
    await insert_preloaded_assistant("new_client_account_plan")
    await insert_preloaded_assistant("lookalike_leads")
    await insert_preloaded_assistant("social_media_writer")
    await insert_preloaded_assistant("sales_call_prep")
    await insert_preloaded_assistant("annual_report_summarizer")
    await insert_preloaded_assistant("meetings_made_easy")
    await insert_preloaded_assistant("general_assistant")
    logger.success("Preloaded assistants inserted successfully")


async def initialize_worker(name: str):
    """
    Initialize a worker group.

    This function sets up the Loki logger and initializes the MongoDB and Qdrant
    databases for a specific worker group.

    Parameters
    ----------
    name : str
        The name of the worker group to initialize.
    """
    await setup_loki_logger()

    logger.info(f"Initializing worker '{name}'...")

    logger.info("Initializing database...")
    await init_db()
    logger.success("Database initialized successfully")

    logger.info("Initializing Qdrant database...")
    await init_qdrant_db()
    logger.success("Qdrant database initialized successfully")
