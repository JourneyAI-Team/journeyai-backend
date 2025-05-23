"""
Redis client utilities.

This module provides standardized Redis clients for both synchronous and
asynchronous usage throughout the application.
"""

import redis
import redis.asyncio as aioredis
from loguru import logger

from app.core.config import settings


class RedisClient:
    """
    Singleton class for managing a synchronous Redis client.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            try:
                cls._instance = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    decode_responses=True,
                    password=settings.REDIS_PASSWORD,
                )
                logger.success("Synchronous Redis client initialized")
            except Exception as e:
                logger.exception(f"Error initializing Redis client: {str(e)}")
                raise
        return cls._instance

    @staticmethod
    def close():
        """
        Close the Redis connection.
        """
        if RedisClient._instance is not None:
            try:
                RedisClient._instance.close()
                RedisClient._instance = None
                logger.success("Synchronous Redis connection closed")
            except Exception as e:
                logger.warning(f"Error closing Redis connection: {str(e)}")


class AsyncRedisClient:
    """
    Singleton class for managing an asynchronous Redis client.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            try:
                cls._instance = aioredis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    decode_responses=True,
                    password=settings.REDIS_PASSWORD,
                )
                logger.success("Asynchronous Redis client initialized")
            except Exception as e:
                logger.exception(f"Error initializing async Redis client: {str(e)}")
                raise
        return cls._instance

    @staticmethod
    async def close():
        """
        Close the asynchronous Redis connection.
        """
        if AsyncRedisClient._instance is not None:
            try:
                await AsyncRedisClient._instance.close()
                AsyncRedisClient._instance = None
                logger.success("Asynchronous Redis connection closed")
            except Exception as e:
                logger.warning(f"Error closing async Redis connection: {str(e)}")


def get_redis_client():
    """
    Get a synchronous Redis client instance.

    Returns
    -------
    redis.Redis
        A Redis client instance.
    """
    return RedisClient()


async def get_redis_async_client():
    """
    Get an asynchronous Redis client instance.

    Returns
    -------
    redis.asyncio.Redis
        An asynchronous Redis client instance.
    """
    return AsyncRedisClient()


async def close_redis_connections():
    """
    Close all Redis connections.

    This function should be called when the application shuts down.
    """
    RedisClient.close()
    await AsyncRedisClient.close()
