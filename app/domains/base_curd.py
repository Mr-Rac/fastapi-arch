from typing import Any, TypeVar, Type, Generic, Optional, Sequence

from sqlalchemy import Select, Insert
from sqlalchemy.ext.asyncio import AsyncSession

M = TypeVar("M")


class Curd(Generic[M]):
    model: Type[M]

    @classmethod
    async def select(cls, session: AsyncSession, stmt: Select, one: bool = True) -> M | Sequence[M]:
        result = await session.execute(stmt)
        result = result.scalars()
        return result.one_or_none() if one else result.all()

    @classmethod
    async def insert(cls, session: AsyncSession, stmt: Insert) -> M:
        return await session.execute(stmt)
