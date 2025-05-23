"""
This module sets up a queue for Python RQ.

It contains all the queues needed for the application in one file.
"""

from rq import Queue

from app.utils.redis_client import get_redis_client

artifacts_queue = Queue("artifacts_queue", connection=get_redis_client())
