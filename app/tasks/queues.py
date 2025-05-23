"""
This module sets up a queue for Python RQ.

It contains all the queues needed for the application in one file.
"""

from redis import Redis
from rq import Queue

from app.core.config import settings

redis_url = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=settings.REDIS_DB,
)
task_queue = Queue("task_queue", connection=redis_url)
