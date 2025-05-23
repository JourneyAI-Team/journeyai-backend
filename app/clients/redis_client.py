"""
Redis client utilities.

This module provides standardized Redis clients for both synchronous and
asynchronous usage throughout the application.
"""

import redis
import redis.asyncio as aioredis
from loguru import logger

from app.core.config import settings

# Singleton instances
_redis_client = None
_redis_async_client = None


def get_redis_client():
    """
    Get a synchronous Redis client instance.

    Returns
    -------
    redis.Redis
        A Redis client instance.
    """
    global _redis_client

    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                password=settings.REDIS_PASSWORD,
            )
            logger.debug("Synchronous Redis client initialized")
        except Exception as e:
            logger.exception(f"Error initializing Redis client: {str(e)}")
            raise

    return _redis_client


async def get_redis_async_client():
    """
    Get an asynchronous Redis client instance.

    Returns
    -------
    redis.asyncio.Redis
        An asynchronous Redis client instance.
    """
    global _redis_async_client

    if _redis_async_client is None:
        try:
            _redis_async_client = await aioredis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                password=settings.REDIS_PASSWORD,
            )
            logger.debug("Asynchronous Redis client initialized")
        except Exception as e:
            logger.exception(f"Error initializing async Redis client: {str(e)}")
            raise

    return _redis_async_client


async def close_redis_connections():
    """
    Close all Redis connections.

    This function should be called when the application shuts down.
    """
    global _redis_client, _redis_async_client

    if _redis_client is not None:
        try:
            _redis_client.close()
            _redis_client = None
            logger.debug("Synchronous Redis connection closed")
        except Exception as e:
            logger.warning(f"Error closing Redis connection: {str(e)}")

    if _redis_async_client is not None:
        try:
            await _redis_async_client.close()
            _redis_async_client = None
            logger.debug("Asynchronous Redis connection closed")
        except Exception as e:
            logger.warning(f"Error closing async Redis connection: {str(e)}")
