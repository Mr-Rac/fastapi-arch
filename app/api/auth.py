from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from app.api.dependencies.redis import get_redis
from app.decorator.auth import skip_auth
from app.schema.auth import *
from app.service.auth import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse, description="login")
@skip_auth()
async def login(
        request: LoginRequest,
        redis: Redis = Depends(get_redis),
        service: AuthService = Depends(AuthService.instance)
):
    return await service.login(request, redis)


@router.post("/logout", response_model=LogoutResponse, description="logout")
@skip_auth()
async def logout(
        request: LogoutRequest,
        redis: Redis = Depends(get_redis),
        service: AuthService = Depends(AuthService.instance)
):
    return await service.logout(request, redis)
