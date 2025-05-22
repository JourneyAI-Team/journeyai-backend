from app.core.config import settings
from rq import Queue
from redis import Redis

redis_url = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=settings.REDIS_DB,
)
task_queue = Queue("task_queue", connection=redis_url)
