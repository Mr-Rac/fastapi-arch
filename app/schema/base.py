from typing import Optional, Any

from fastapi import status
from pydantic import BaseModel, Field

from app.exception import ERR


class BaseResponse(BaseModel):
    code: int = Field(default=status.HTTP_200_OK, description="error code")
    message: str = Field(default=ERR.SUCCESS, description="message")
    data: Optional[Any] = Field(default=None, description="data")
