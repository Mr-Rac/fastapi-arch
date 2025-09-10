from datetime import datetime

from pydantic import Field

from app.domains.base_schema import BaseData, BaseRequest, BaseResponse


class LoginData(BaseData):
    access_token: str | None = Field(default=None, description="access token")
    refresh_token: str | None = Field(default=None, description="refresh token")
    token_type: str = Field(default="Bearer", description="token type")


class LoginRequest(BaseRequest):
    username: str = Field(..., description="username")
    password: str = Field(..., description="password")


class LoginResponse(BaseResponse):
    data: LoginData | None = Field(default=None, description="login data")


class LogoutRequest(BaseRequest):
    username: str = Field(..., description="username")


class LogoutResponse(BaseResponse):
    pass


class UserData(BaseData):
    id: int | None = Field(default=None, description="id")
    username: str | None = Field(default=None, description="username")
    created_at: datetime | None = Field(default=None, description="created at")
    updated_at: datetime | None = Field(default=None, description="updated at")


class CreateUserRequest(BaseRequest):
    username: str = Field(..., description="username")
    password: str = Field(..., description="password")


class CreateUserResponse(BaseResponse):
    data: UserData | None = Field(default=None, description="create user data")
