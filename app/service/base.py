from typing import Callable, Awaitable, TypeVar

from fastapi import status, HTTPException
from loguru import logger

from app.exception import ERR
from app.schema.base import BaseResponse

T = TypeVar("T", bound=BaseResponse)


class BaseService:
    _instances = {}

    @classmethod
    def instance(cls):
        if cls not in cls._instances:
            cls._instances[cls] = cls()
        return cls._instances[cls]

    async def safe_execute(
            self,
            func: Callable[..., Awaitable[T]],
            *args,
            **kwargs,
    ) -> T:
        try:
            return await func(*args, **kwargs)

        except HTTPException as e:
            logger.warning(f"{func.__name__} HTTPException: {e.detail}")
            return self._make_response(
                e.status_code,
                e.detail
            )

        except Exception as e:
            logger.exception(f"{func.__name__} unknown error")
            return self._make_response(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                str(e) or ERR.FAILURE,
            )

    def _make_response(self, code: int, message: str, data=None):
        return BaseResponse(code=code, message=message, data=data)
