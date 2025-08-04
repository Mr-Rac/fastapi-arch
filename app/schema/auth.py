from typing import Optional

from pydantic import BaseModel, Field

from app.schema.base import BaseResponse


class LoginData(BaseModel):
    access_token: Optional[str] = Field(default=None, description="access token")
    refresh_token: Optional[str] = Field(default=None, description="refresh token")


class LoginRequest(BaseModel):
    username: str = Field(..., description="username")
    password: str = Field(..., description="password")


class LoginResponse(BaseResponse):
    data: LoginData = Field(default=LoginData(), description="user info")


class LogoutRequest(BaseModel):
    username: str = Field(..., description="username")


class LogoutResponse(BaseResponse):
    pass
