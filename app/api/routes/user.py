from fastapi import APIRouter, Depends

from app.api.dependencies.mysql import AuthMySQLDep
from app.domains.base_schema import BaseResponse
from app.domains.user.schema import *
from app.domains.user.service import UserService

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/create", response_model=BaseResponse, description="create user")
async def create_user(
        body: UserCreate,
        mysql: AuthMySQLDep,
        service: UserService = Depends(UserService.instance)
) -> BaseResponse:
    return await service.safe_execute(service.create, mysql, body)


@router.post("/update", response_model=BaseResponse, description="create user")
async def create_user(
        body: UserUpdate,
        mysql: AuthMySQLDep,
        service: UserService = Depends(UserService.instance)
) -> BaseResponse:
    return await service.safe_execute(service.update, mysql, body)
