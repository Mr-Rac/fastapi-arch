from redis.asyncio import Redis

from app.core.setting import settings


async def create_redis_client() -> Redis:
    return Redis.from_url(
        url=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
        decode_responses=settings.REDIS_DECODE_RESPONSES,
        max_connections=settings.REDIS_MAX_CONNECTIONS,
        retry_on_timeout=settings.REDIS_RETRY_ON_TIMEOUT,
    )


async def close_redis_client(redis: Redis) -> None:
    await redis.aclose()
