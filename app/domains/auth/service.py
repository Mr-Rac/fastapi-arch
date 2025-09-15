from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.const import TokenType
from app.domains.auth.schema import *
from app.domains.auth.token import Token
from app.domains.base_service import BaseService
from app.domains.user.curd import UserCurd
from app.models.auth import User


class AuthService(BaseService):

    @staticmethod
    async def login(
            form: Annotated[OAuth2PasswordRequestForm, Depends()],
            mysql: AsyncSession,
            redis: Redis,
    ) -> LoginData:
        user = await UserCurd.authenticate(mysql, form.username, form.password)
        return LoginData(
            access_token=await Token.create(TokenType.ACCESS, user.username, redis),
            refresh_token=await Token.create(TokenType.REFRESH, user.username, redis),
            token_type="Bearer",
        )

    @staticmethod
    async def logout(
            body: LogoutRequest,
            mysql: AsyncSession,
            redis: Redis,
    ) -> BaseData:
        user: User = await UserCurd.get_by_username(mysql, body.username)
        await Token.clear(user.username, redis)
        return BaseData()
