from pydantic import Field

from app.domains.base_schema import BaseData, BaseRequest, BaseResponse


class UserData(BaseData):
    username: str | None = Field(default=None, description="username")


class CreateRequest(BaseRequest):
    username: str = Field(..., description="username")
    password: str = Field(..., description="password")


class CreateResponse(BaseResponse):
    data: UserData | None = Field(default=None, description="user data")
