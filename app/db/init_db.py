from beanie import init_beanie
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.models.account import Account
from app.models.message import Message
from app.models.organization import Organization
from app.models.session import Session


async def init_db():
    """
    Initialize database connection and register document models
    """
    if not settings.MONGODB_URL:
        logger.warning("MONGODB_URL is not set. Using default MongoDB URL.")
        mongodb_url = "mongodb://localhost:27017"
    else:
        mongodb_url = str(settings.MONGODB_URL)

    # Create motor client
    client = AsyncIOMotorClient(mongodb_url)

    # Initialize beanie with the document models
    await init_beanie(
        database=client[settings.MONGODB_DB_NAME],
        document_models=[
            Account,
            Organization,
            Session,
            Message,
        ],
    )

    logger.info("Database initialized successfully")
