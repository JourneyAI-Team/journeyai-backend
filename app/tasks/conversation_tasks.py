import os

from app.tasks.worker import celery_app

# Testing Variables
USE_TEST_DATA_FOR_INGESTION: bool = (
    os.getenv("USE_TEST_DATA_FOR_INGESTION", "false").lower() == "true"
)


@celery_app.task(name="ingest_message")
async def ingest_message(message_id: str):
    pass
