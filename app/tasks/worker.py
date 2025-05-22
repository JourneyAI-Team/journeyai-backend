import os

from celery import Celery

from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "journeyai_worker",
    broker=f"redis://default:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    backend=f"redis://default:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    include=[
        "app.tasks.conversation_tasks",
        "app.tasks.notification_tasks",
        "app.tasks.artifact_tasks",
        # Add more task modules here
    ],
)

# Optional configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,  # Results expire after 1 hour
    worker_prefetch_multiplier=1,  # Disable prefetching
    worker_concurrency=os.cpu_count(),  # Use all available CPU cores
)


if __name__ == "__main__":
    celery_app.start()
