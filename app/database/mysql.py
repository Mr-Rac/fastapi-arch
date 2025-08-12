from aiomysql import create_pool, Pool

from app.core.setting import settings


async def create_mysql_pool() -> Pool:
    return await create_pool(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        db=settings.MYSQL_DB,
        minsize=settings.MYSQL_MINSIZE,
        maxsize=settings.MYSQL_MAXSIZE,
        autocommit=settings.MYSQL_AUTO_COMMIT,
        pool_recycle=settings.MYSQL_POOL_RECYCLE,
        connect_timeout=settings.MYSQL_CONNECT_TIMEOUT,
        echo=settings.MYSQL_ECHO,
    )
