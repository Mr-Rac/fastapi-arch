from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.mysql import AuthMySQLDep
from app.api.dependencies.redis import AuthRedisDep
from app.domains.auth.schema import *
from app.domains.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse, description="login")
async def login(
        form: Annotated[OAuth2PasswordRequestForm, Depends()],
        mysql: AuthMySQLDep,
        redis: AuthRedisDep,
        service: AuthService = Depends(AuthService.instance)
) -> LoginResponse:
    return await service.safe_execute(service.login, form, mysql, redis)


@router.post("/logout", response_model=LogoutResponse, description="logout")
async def logout(
        body: LogoutRequest,
        mysql: AuthMySQLDep,
        redis: AuthRedisDep,
        service: AuthService = Depends(AuthService.instance)
) -> LogoutResponse:
    return await service.safe_execute(service.logout, body, mysql, redis)
