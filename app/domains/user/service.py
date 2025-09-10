from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.user.schema import *
from app.domains.base_service import BaseService
from app.domains.user.curd import UserCurd


class UserService(BaseService):

    @staticmethod
    async def create(
            body: CreateRequest,
            mysql: AsyncSession,
    ) -> UserData:
        try:
            user = await UserCurd.create(mysql, body.username, body.password)
            await mysql.commit()
        except:
            await mysql.rollback()
            raise
        return UserData(
            username=user.username,
        )
