import asyncio

from arq import create_pool
from arq.connections import ArqRedis, RedisSettings
from loguru import logger

from app.core.config import settings

_arq_redis: ArqRedis | None = None
_lock = asyncio.Lock()


async def get_arq() -> ArqRedis:
    global _arq_redis

    if _arq_redis is None:
        async with _lock:
            if _arq_redis is None:  # Double-checked locking
                _arq_redis = await create_pool(
                    RedisSettings(
                        host=settings.REDIS_HOST,
                        port=settings.REDIS_PORT,
                        password=settings.REDIS_PASSWORD,
                        database=settings.REDIS_DB,
                    )
                )
                logger.success("Initialized ARQ Redis pool")

    return _arq_redis
