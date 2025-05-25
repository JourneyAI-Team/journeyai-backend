from arq.connections import RedisSettings

from app.clients.arq_client import get_arq
from app.core.config import settings
from app.core.starters import initialize_worker
from app.workers.agents.tasks import process_session

# Worker Configuration
NAME = "agents"
FUNCTIONS = [process_session]


# Setup function
async def startup(ctx):

    ctx["arq"] = await get_arq()

    await initialize_worker(NAME)


class WorkerSettings:
    functions = FUNCTIONS
    on_startup = startup
    redis_settings = RedisSettings(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        database=settings.REDIS_DB,
    )
    queue_name = NAME
