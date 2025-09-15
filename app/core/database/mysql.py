from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel

from app.core.config import settings
from app.domains.user.curd import UserCurd
from app.domains.user.schema import UserCreate


async def create_auth_mysql_engine() -> AsyncEngine:
    return create_async_engine(
        settings.MYSQL_AUTH_DB_URL,
        echo=settings.MYSQL_ECHO,
        echo_pool=settings.MYSQL_ECHO,
        isolation_level=settings.MYSQL_ISOLATION_LEVEL,
        max_overflow=settings.MYSQL_MAX_OVERFLOW,
        pool_pre_ping=settings.MYSQL_POOL_PRE_PING,
        pool_size=settings.MYSQL_POOL_SIZE,
        pool_recycle=settings.MYSQL_POOL_RECYCLE,
        pool_timeout=settings.MYSQL_POOL_TIMEOUT,
    )


async def create_auth_mysql_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )


async def init_auth_mysql(session: AsyncSession) -> None:
    try:
        await UserCurd.get_by_username(session, settings.ADMIN_USERNAME)
    except:
        user_in = UserCreate(
            username=settings.ADMIN_USERNAME,
            password=settings.ADMIN_PASSWORD,
        )
        await UserCurd.create(session, user_in)
