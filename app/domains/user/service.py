from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.base_service import BaseService
from app.domains.user.curd import UserCurd
from app.domains.user.schema import *


class UserService(BaseService):

    @staticmethod
    async def create(mysql: AsyncSession, user_in: UserCreate) -> UserPublic:
        user = await UserCurd.create(mysql, user_in)
        return UserPublic.model_validate(user)

    @staticmethod
    async def update(mysql: AsyncSession, user_in: UserUpdate) -> UserPublic:
        user = await UserCurd.update(mysql, user_in)
        return UserPublic.model_validate(user)
