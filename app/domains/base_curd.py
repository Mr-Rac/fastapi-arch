from typing import TypeVar, Type, Generic, Sequence

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

M = TypeVar("M")


class Curd(Generic[M]):
    model: Type[M]

    @classmethod
    async def select(cls, session: AsyncSession, stmt: Select, one: bool = True) -> M | Sequence[M]:
        result = await session.execute(stmt)
        result = result.scalars()
        return result.one_or_none() if one else result.all()
