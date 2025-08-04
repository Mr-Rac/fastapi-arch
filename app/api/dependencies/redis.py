from typing import Optional

from aioredis import Redis
from fastapi import Request, HTTPException, status

from app.exception import ERR


async def get_redis(request: Request) -> Redis:
    redis: Optional[Redis] = getattr(request.app.state, "redis", None)
    if not redis:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=ERR.DEPENDENCY_REDIS_INVALID)
    return redis
