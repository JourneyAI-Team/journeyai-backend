from arq.connections import RedisSettings
from loguru import logger

from app.clients.arq_client import close_arq_pool, get_arq
from app.clients.redis_client import close_redis_connections
from app.core.config import settings
from app.core.starters import initialize_worker
from app.workers.sessions.tasks import check_and_title_session

# Worker Configuration
NAME = "sessions"
FUNCTIONS = [check_and_title_session]


# Setup function
async def startup(ctx):

    ctx["arq"] = await get_arq()

    await initialize_worker(NAME)


# Shutdown function
async def shutdown(ctx):
    """
    Clean up resources when the worker shuts down.

    This function closes all Redis connections to prevent
    connection leaks when the worker is terminated.
    """
    try:
        # Close ARQ Redis pool
        await close_arq_pool()

        # Close regular Redis connections
        await close_redis_connections()

        logger.success(f"Worker '{NAME}' shutdown completed successfully")
    except Exception as e:
        logger.warning(f"Error during worker '{NAME}' shutdown: {str(e)}")


class WorkerSettings:
    functions = FUNCTIONS
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        database=settings.REDIS_DB,
    )
    queue_name = NAME
