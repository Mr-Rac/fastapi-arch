from typing import AsyncGenerator

from aiomysql import Pool, Cursor
from fastapi import Request, HTTPException, status, Depends

from app.exception import ERR


async def get_mysql_pool(request: Request) -> Pool:
    pool: Pool | None = getattr(request.app.state, "mysql_pool", None)
    if not pool:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=ERR.DEPENDENCY_MYSQL_INVALID)
    return pool


async def get_mysql(pool: Pool = Depends(get_mysql_pool)) -> AsyncGenerator[Cursor, None]:
    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            yield cursor
