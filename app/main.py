import asyncio
import logging
import ssl
import sys
from contextlib import asynccontextmanager
from datetime import timedelta

import aiohttp
import certifi
from aiomysql import Pool
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from redis.asyncio import Redis

from app.api import routers
from app.core.setting import settings
from app.database.mysql import create_mysql_pool, close_mysql_pool
from app.database.redis import create_redis_client, close_redis_client
from app.exception.http_exception import http_exception_handler
from app.middleware.auth import AuthMiddleware


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except Exception:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


logging.root.handlers = [InterceptHandler()]
logging.root.setLevel(settings.LOG_LEVEL)


def _replace_uvicorn_logger_handlers():
    uvicorn_related_loggers = [
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "uvicorn.lifespan",
        "uvicorn.server",
    ]
    for logger_name in uvicorn_related_loggers:
        log = logging.getLogger(logger_name)
        log.handlers.clear()
        log.addHandler(InterceptHandler())
        log.propagate = False


def _init_log():
    logger.remove()

    if not settings.is_local:
        logger.add(
            "log/ji_admin_{time:YYYY-MM-DD}.log",
            rotation=timedelta(days=settings.LOG_ROTATION),
            retention=timedelta(weeks=settings.LOG_RETENTION),
            compression="zip",
            encoding="utf-8",
            enqueue=True,
            backtrace=True,
            diagnose=True,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            level=settings.LOG_LEVEL,
        )

    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        backtrace=True,
        diagnose=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
    )

    _replace_uvicorn_logger_handlers()


async def task_init_aiohttp(app: FastAPI, retry_interval: int = 5):
    session: aiohttp.ClientSession | None = None
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    _test_url = "https://httpbin.org/get"

    while True:
        try:
            session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=settings.AIOHTTP_TIMEOUT),
                connector=aiohttp.TCPConnector(ssl=ssl_context),
            )

            async with session.get(_test_url) as response:
                response.raise_for_status()
            app.state.aiohttp_session = session
            logger.warning("Aiohttp session initialized.")

            return
        except Exception as e:
            logger.error(f"Aiohttp session initialize failed: {e}, retrying...")

            if session:
                await session.close()
                session = None

        await asyncio.sleep(retry_interval)


async def task_connect_redis(app: FastAPI, retry_interval: int = 5):
    redis: Redis | None = None

    while True:
        try:
            redis = await create_redis_client()

            await redis.ping()
            app.state.redis = redis
            logger.warning("Redis connected.")

            return
        except Exception as e:
            logger.error(f"Redis connect failed: {e}, retrying...")

            if redis:
                await close_redis_client(redis)
                redis = None

        await asyncio.sleep(retry_interval)


async def task_connect_mysql(app: FastAPI, retry_interval: int = 5):
    pool: Pool | None = None

    while True:
        try:
            pool = await create_mysql_pool()

            async with pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute("SELECT 1")
                    await cursor.fetchone()
            app.state.mysql_pool = pool
            logger.warning("MySQL connected.")

            return
        except Exception as e:
            logger.error(f"MySQL connect failed: {e}, retrying...")

            if pool:
                await close_mysql_pool(pool)
                pool = None

        await asyncio.sleep(retry_interval)


def _cleanup_task(task: asyncio.Task):
    try:
        app.state.background_tasks.remove(task)
        logger.warning(f"Task {task.get_name()} removed.")
    except ValueError:
        pass


async def _shutdown(app: FastAPI):
    if getattr(app.state, "background_tasks", []):
        for task in app.state.background_tasks:
            task.cancel()
            try:
                await task
                logger.warning(f"Task {task.get_name()} canceled.")
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"Failed to cancel task {task.get_name()}: {e}")

    if getattr(app.state, "mysql_pool", None):
        try:
            await close_mysql_pool(app.state.mysql_pool)
            logger.warning(f"MySQL pool closed.")
        except Exception as e:
            logger.error(f"Failed to close mysql pool: {e}")

    if getattr(app.state, "redis", None):
        try:
            await close_redis_client(app.state.redis)
            logger.warning("Redis closed.")
        except Exception as e:
            logger.error(f"Failed to close redis client: {e}")

    if getattr(app.state, "aiohttp_session", None):
        try:
            await app.state.aiohttp_session.close()
            logger.warning("Aiohttp session closed.")
        except Exception as e:
            logger.error(f"Failed to close aiohttp session: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        _init_log()

        app.state.background_tasks: list[asyncio.Task] = []
        app.state.aiohttp_session: aiohttp.ClientSession | None = None
        app.state.redis: Redis | None = None
        app.state.mysql_pool: Pool | None = None

        background_tasks = [
            asyncio.create_task(task_init_aiohttp(app), name="init-aiohttp"),
            asyncio.create_task(task_connect_redis(app), name="connect-redis"),
            asyncio.create_task(task_connect_mysql(app), name="connect-mysql"),
        ]
        for task in background_tasks:
            task.add_done_callback(_cleanup_task)
            app.state.background_tasks.append(task)

        logger.info("Application initialized completed.")
    except Exception as e:
        await _shutdown(app)
        logger.critical(f"Application initialization failed: {e}")
        raise

    try:
        yield
    finally:
        await _shutdown(app)
        logger.info("Application shutdown completed.")


def create_app(enable_lifespan: bool = True) -> FastAPI:
    app = FastAPI(
        title=settings.SERVER_NAME,
        lifespan=lifespan if enable_lifespan else None,
    )
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    app.add_middleware(AuthMiddleware)
    for router in routers:
        app.include_router(router)
    return app


app = create_app()
