import logging
import ssl
import sys
from contextlib import asynccontextmanager
from datetime import timedelta

import aiohttp
import certifi
import redis.asyncio as Redis
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api import routers
from app.core.setting import settings
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        _init_log()
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        app.state.aiohttp_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=settings.AIOHTTP_TIMEOUT),
            connector=aiohttp.TCPConnector(ssl=ssl_context),
        )
        app.state.redis = Redis.from_url(
            url=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=settings.REDIS_DECODE_RESPONSES,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            retry_on_timeout=settings.REDIS_RETRY_ON_TIMEOUT,
        )
        logger.info("Application initialized completed.")
    except Exception as e:
        logger.critical(f"Application initialization failed: {e}")
        raise

    try:
        yield
    finally:
        await app.state.aiohttp_session.close()
        await app.state.redis.close()
        await app.state.redis.connection_pool.disconnect()
        logger.info("Application shutdown completed.")


def create_app(enable_lifespan: bool = True) -> FastAPI:
    app = FastAPI(
        title=f"official_server_{settings.SERVER_NAME}",
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
