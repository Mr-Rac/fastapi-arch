from fastapi import Request, HTTPException, status
from redis.asyncio import Redis

from app.exception import ERR


async def get_redis(request: Request) -> Redis:
    redis: Redis | None = getattr(request.app.state, "redis", None)
    if not redis:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=ERR.DEPENDENCY_REDIS_INVALID)
    return redis
