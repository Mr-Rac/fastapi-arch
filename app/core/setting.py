from typing import Literal, Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # Base
    SERVER_ENV: Literal["PROD", "TEST", "LOCAL"] = "LOCAL"
    SERVER_NAME: str = "fastapi-app"

    # Log
    LOG_LEVEL: str = "INFO"
    LOG_ROTATION: int = 1  # 单位: 天
    LOG_RETENTION: int = 7  # 单位: 天

    # MySQL
    MYSQL_HOST: str
    MYSQL_PORT: int = 3306
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_POOL_SIZE: int = 10
    MYSQL_MAX_OVERFLOW: int = 20
    MYSQL_POOL_PRE_PING: bool = True
    MYSQL_POOL_RECYCLE: int = 3600
    MYSQL_POOL_TIMEOUT: int = 30
    MYSQL_PAGE_LIMIT: int = 100

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_USER: Optional[str] = None
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_DECODE_RESPONSES: bool = True
    REDIS_MAX_CONNECTIONS: int = 10
    REDIS_RETRY_ON_TIMEOUT: bool = True

    # JWT
    JWT_TYPE: str = "Bearer"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    JWT_ACCESS_TOKEN_EXPIRE: int = 60 * 10  # 单位: 秒
    JWT_REFRESH_TOKEN_EXPIRE: int = 60 * 60 * 24  # 单位: 秒

    # Aiohttp
    AIOHTTP_TIMEOUT: int = 30  # 请求超时秒数

    # Pydantic
    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }

    @property
    def is_prod(self) -> bool:
        return self.SERVER_ENV == "PROD"

    @property
    def is_test(self) -> bool:
        return self.SERVER_ENV == "TEST"

    @property
    def is_local(self) -> bool:
        return self.SERVER_ENV == "LOCAL"


settings = Settings()
