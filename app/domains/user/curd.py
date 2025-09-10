from passlib.context import CryptContext
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.base_curd import Curd
from app.domains.user.exception import UserError
from app.models.auth import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCurd(Curd):

    @classmethod
    async def create(cls, session: AsyncSession, username: str, password: str) -> User:
        stmt = insert(User).values(username=username, password_hash=pwd_context.hash(password))
        try:
            await cls.insert(session, stmt)
        except IntegrityError as exc:
            raise Exception(exc.args[0])
        except:
            raise
        user = await cls.get_by_username(session, username)
        return user

    @classmethod
    async def get_by_username(cls, session: AsyncSession, username: str) -> User:
        stmt = select(User).where(User.username == username)
        user = await cls.select(session, stmt)
        if not user:
            raise Exception(UserError.NOT_FOUND)
        return user

    @classmethod
    async def authenticate(cls, session: AsyncSession, username: str, password: str) -> User:
        user = await cls.get_by_username(session, username)
        if not pwd_context.verify(password, user.password_hash):
            raise Exception(UserError.INCORRECT_PASSWORD)
        return user
