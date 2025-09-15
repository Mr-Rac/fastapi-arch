from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.base_curd import Curd
from app.domains.user.exception import UserError
from app.domains.user.schema import UserCreate, UserUpdate
from app.models.auth import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCurd(Curd):

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

    @classmethod
    async def create(cls, session: AsyncSession, user_in: UserCreate) -> User:
        try:
            user = User.model_validate(
                user_in,
                update={
                    "password": pwd_context.hash(user_in.password),
                }
            )
            session.add(user)
        except IntegrityError as exc:
            await session.rollback()
            raise Exception(exc.args[0])
        except:
            await session.rollback()
            raise
        await session.commit()
        await session.refresh(user)
        return user

    @classmethod
    async def update(cls, session: AsyncSession, user_in: UserUpdate) -> User:
        try:
            user = await cls.get_by_username(session, user_in.username)
            user.sqlmodel_update(
                user_in.model_dump(exclude_unset=True),
                update={
                    "password": pwd_context.hash(user_in.password),
                } if user_in.password else {},
            )
        except IntegrityError as exc:
            await session.rollback()
            raise Exception(exc.args[0])
        except:
            await session.rollback()
            raise
        await session.commit()
        await session.refresh(user)
        return user
