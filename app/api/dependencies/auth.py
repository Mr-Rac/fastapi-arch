import json
from asyncio import gather
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

from aioredis import Redis
from fastapi import HTTPException, status
from jwcrypto import jwt, jwk

from app.core.setting import settings
from app.exception import ERR
from app.utils.redis_key.auth import AUTH_TOKEN_KEY

SUB_KEY: str = "sub"


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenService:
    _keys = {
        TokenType.ACCESS: jwk.JWK.from_password(settings.JWT_ACCESS_SECRET_KEY),
        TokenType.REFRESH: jwk.JWK.from_password(settings.JWT_REFRESH_SECRET_KEY),
    }

    _expirations = {
        TokenType.ACCESS: settings.JWT_ACCESS_TOKEN_EXPIRE,
        TokenType.REFRESH: settings.JWT_REFRESH_TOKEN_EXPIRE,
    }

    @classmethod
    async def create_token(cls, token_type: TokenType, payload: dict, redis: Redis) -> str:
        key = cls._keys[token_type]
        expire = datetime.now(timezone.utc) + timedelta(seconds=cls._expirations[token_type])
        payload.update({"exp": int(expire.timestamp())})

        token = jwt.JWT(header={"alg": "HS256"}, claims=payload)
        token.make_signed_token(key)
        encoded_token = token.serialize()

        redis_key = AUTH_TOKEN_KEY.format(token_type.value, payload[SUB_KEY])
        await redis.setex(redis_key, cls._expirations[token_type], encoded_token)
        return encoded_token

    @classmethod
    async def verify_token(cls, token: str, token_type: TokenType, redis: Redis) -> dict:
        key = cls._keys[token_type]

        try:
            token_obj = jwt.JWT(key=key, jwt=token)
            claims = json.loads(token_obj.claims)
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ERR.TOKEN_INVALID)

        sub = claims.get(SUB_KEY)
        if not sub:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ERR.TOKEN_SUB_MISSING)

        redis_key = AUTH_TOKEN_KEY.format(token_type.value, sub)
        cached_token = await redis.get(redis_key)
        if not cached_token:
            raise HTTPException(status_code=status.HTTP_410_GONE, detail=ERR.TOKEN_EXPIRED)
        if cached_token != token:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERR.TOKEN_MISMATCH)

        return claims

    @classmethod
    async def clear_tokens(cls, sub: str, redis: Redis):
        await gather(
            redis.delete(AUTH_TOKEN_KEY.format(TokenType.ACCESS.value, sub)),
            redis.delete(AUTH_TOKEN_KEY.format(TokenType.REFRESH.value, sub)),
        )

    @staticmethod
    def extract_token(header_value: Optional[str]) -> Optional[str]:
        if not header_value:
            return None

        parts = header_value.strip().split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        return parts[1]
