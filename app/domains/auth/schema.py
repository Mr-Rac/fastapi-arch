from pydantic import Field

from app.domains.base_schema import BaseData, BaseRequest


class LoginData(BaseData):
    access_token: str | None = Field(default=None, description="access token")
    refresh_token: str | None = Field(default=None, description="refresh token")
    token_type: str = Field(default="Bearer", description="token type")


class LogoutRequest(BaseRequest):
    username: str = Field(..., description="username")
