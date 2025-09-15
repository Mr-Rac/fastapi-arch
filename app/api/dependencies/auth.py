from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from pydantic import ValidationError
from redis.asyncio import Redis
from sqlalchemy import select

from app.core.config import settings
from app.domains.auth.const import TokenType
from app.domains.auth.exception import AuthError
from app.domains.auth.token import Token

OAuth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}/auth/login/access-token",
    refreshUrl=f"{settings.API_PREFIX}/auth/login/refresh-token",
)


async def get_current_user(
        token: Annotated[str, Depends(OAuth2)],
        session: Annotated[Cursor, Depends(get_mysql)],
        redis: Annotated[Redis, Depends(get_redis)],
) -> User:
    try:
        payload = await Token.verify(token, TokenType.ACCESS, redis)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AuthError.EXPIRED,
        )
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=AuthError.INVALID,
        )
    stmt = select(User).where(User.username == payload.sub)
    await session.execute(stmt)
    user = session.fetchone()
    return user


def get_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user
