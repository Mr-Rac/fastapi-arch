import redis.asyncio as Redis

from app.api.dependencies.auth import TokenService, TokenType
from app.schema.auth import *
from app.service.base import BaseService


class AuthService(BaseService):

    @staticmethod
    async def _login(payload: dict, redis: Redis) -> LoginResponse:
        return LoginResponse(
            data=LoginData(
                access_token=await TokenService.create_token(TokenType.ACCESS, payload, redis),
                refresh_token=await TokenService.create_token(TokenType.REFRESH, payload, redis),
            )
        )

    @staticmethod
    async def _logout(username: str, redis: Redis):
        await TokenService.clear_tokens(username, redis)
        return LogoutResponse()

    async def login(self, request: LoginRequest, redis: Redis):
        payload = {
            "sub": request.username,
        }
        return await self.safe_execute(self._login, payload, redis)

    async def logout(self, request: LogoutRequest, redis: Redis):
        sub = request.username
        return await self.safe_execute(self._logout, sub, redis)
