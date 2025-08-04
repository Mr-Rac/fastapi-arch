from fastapi import Request, status, HTTPException
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.api.dependencies.auth import TokenService, TokenType
from app.api.dependencies.redis import get_redis
from app.core.setting import settings
from app.exception import ERR


def unauthorized_response(message: str, code: int = status.HTTP_401_UNAUTHORIZED) -> JSONResponse:
    return JSONResponse(
        status_code=code,
        headers={"WWW-Authenticate": "Bearer"},
        content={"code": code, "message": message},
    )


def server_error_response(message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers={"WWW-Authenticate": "Bearer"},
        content={"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": message},
    )


class AuthMiddleware(BaseHTTPMiddleware):
    __ACCESS_TOKEN_HEADER = "Authorization"
    __REFRESH_TOKEN_HEADER = "Authorization-Refresh"
    __NEW_ACCESS_TOKEN_HEADER = "Authorization-New"

    async def dispatch(self, request: Request, call_next):

        if settings.is_local:
            return await call_next(request)

        route: APIRoute = request.scope.get("route")
        endpoint = getattr(route, "endpoint", None)

        if endpoint and getattr(endpoint, "_skip_auth", False):
            return await call_next(request)

        try:
            access_token = TokenService.extract_token(request.headers.get(self.__ACCESS_TOKEN_HEADER))
            if not access_token:
                return unauthorized_response(ERR.TOKEN_HEADER_MISSING.format(self.__ACCESS_TOKEN_HEADER))
            payload = await TokenService.verify_token(access_token, TokenType.ACCESS, await get_redis(request))
            request.state.user = payload
        except HTTPException as e:
            if e.status_code == status.HTTP_410_GONE:
                try:
                    redis = await get_redis(request)
                    refresh_token = TokenService.extract_token(request.headers.get(self.__REFRESH_TOKEN_HEADER))
                    if not refresh_token:
                        return unauthorized_response(ERR.TOKEN_HEADER_MISSING.format(self.__REFRESH_TOKEN_HEADER))
                    payload = await TokenService.verify_token(refresh_token, TokenType.REFRESH, redis)
                    new_access_token = await TokenService.create_token(TokenType.ACCESS, payload, redis)
                    request.state.user = payload
                    request.state.new_access_token = new_access_token
                except HTTPException as e:
                    return unauthorized_response(e.detail, e.status_code)
                except Exception as e:
                    return server_error_response(str(e))
            else:
                return unauthorized_response(e.detail, e.status_code)
        except Exception as e:
            return server_error_response(str(e))

        response = await call_next(request)

        if hasattr(request.state, "new_access_token"):
            response.headers[self.__NEW_ACCESS_TOKEN_HEADER] = request.state.new_access_token

        return response
