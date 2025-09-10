from asyncio import gather
from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from pydantic import BaseModel, field_validator
from redis.asyncio import Redis

from app.domains.auth.const import TokenType
from app.core.config import settings
from app.domains.auth.exception import AuthError
from app.domains.auth.redis_key import AUTH_TOKEN_KEY

ALGORITHM = "HS256"


class Payload(BaseModel):
    sub: str
    exp: int

    @property
    def expire_at(self) -> datetime:
        return datetime.fromtimestamp(self.exp, tz=timezone.utc)

    @field_validator("exp", mode="before")
    def normalize_exp(cls, v: int | datetime) -> int:
        if isinstance(v, datetime):
            return int(v.timestamp())
        return v

    @field_validator("exp")
    def check_exp(cls, v: int) -> int:
        if v < int(datetime.now(tz=timezone.utc).timestamp()):
            raise ValueError(AuthError.EXPIRED)
        return v


class Token:
    _expirations = {
        TokenType.ACCESS: settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        TokenType.REFRESH: settings.REFRESH_TOKEN_EXPIRE_SECONDS,
    }

    @classmethod
    async def create(cls, token_type: TokenType, subject: str, redis: Redis) -> str:
        expire = datetime.now(timezone.utc) + timedelta(seconds=cls._expirations[token_type])
        payload = Payload(sub=subject, exp=int(expire.timestamp()))
        encoded_jwt = jwt.encode(payload.model_dump(), settings.SECRET_KEY, algorithm=ALGORITHM)
        redis_key = AUTH_TOKEN_KEY.format(token_type.value, subject)
        await redis.setex(redis_key, cls._expirations[token_type], encoded_jwt)
        return encoded_jwt

    @classmethod
    async def verify(cls, token: str, token_type: TokenType, redis: Redis) -> Payload:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        payload = Payload.model_validate(payload)
        redis_key = AUTH_TOKEN_KEY.format(token_type.value, payload.sub)
        cached_token = await redis.get(redis_key)
        if isinstance(cached_token, bytes):
            cached_token = cached_token.decode()
        if not cached_token:
            raise ExpiredSignatureError()
        if cached_token != token:
            raise InvalidTokenError()
        return payload

    @classmethod
    async def refresh(cls, token: str, redis: Redis) -> str:
        payload = await cls.verify(token, TokenType.REFRESH, redis)
        new_token = await cls.create(TokenType.ACCESS, payload.sub, redis)
        return new_token

    @classmethod
    async def clear(cls, subject: str, redis: Redis):
        await gather(
            redis.delete(AUTH_TOKEN_KEY.format(TokenType.ACCESS.value, subject)),
            redis.delete(AUTH_TOKEN_KEY.format(TokenType.REFRESH.value, subject)),
        )

    @staticmethod
    def extract(header_value: str | None) -> str | None:
        if not header_value:
            return None
        parts = header_value.strip().split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        return parts[1]
