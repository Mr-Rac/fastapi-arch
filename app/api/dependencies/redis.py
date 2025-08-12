from typing import Optional

import redis.asyncio as Redis
from fastapi import Request, HTTPException, status

from app.exception import ERR


async def get_redis(request: Request) -> Redis:
    redis: Optional[Redis] = getattr(request.app.state, "redis", None)
    if not redis:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=ERR.DEPENDENCY_REDIS_INVALID)
    return redis
