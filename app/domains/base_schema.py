from typing import Any

from fastapi import status
from pydantic import BaseModel, Field, ConfigDict

from app.domains.base_exception import Error


class BaseData(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseRequest(BaseModel):
    ...


class BaseResponse(BaseModel):
    status_code: int = Field(default=status.HTTP_200_OK, description="status code")
    detail: str = Field(default=Error.SUCCESS, description="detail")
    data: Any | None = Field(default=None, description="data")
