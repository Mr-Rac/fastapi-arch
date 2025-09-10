from fastapi import APIRouter, Depends

from app.api.dependencies.mysql import AuthMySQLDep
from app.domains.user.schema import *
from app.domains.user.service import UserService

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/create", response_model=CreateResponse, description="create user")
async def create_user(
        body: CreateRequest,
        mysql: AuthMySQLDep,
        service: UserService = Depends(UserService.instance)
) -> CreateResponse:
    return await service.safe_execute(service.create, body, mysql)
