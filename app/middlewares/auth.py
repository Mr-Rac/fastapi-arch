from fastapi import Request, status, HTTPException
from jwt import ExpiredSignatureError, InvalidTokenError
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

from app.api.dependencies.redis import get_redis
from app.domains.auth.const import TokenType, TokenHeader
from app.core.config import settings
from app.domains.auth.token import Token
from app.domains.base_exception import CommonException
from app.domains.auth.exception import TokenException, AuthError

_WHITE_URL = {
    f"{settings.API_PREFIX}/openapi.json",
    f"{settings.API_PREFIX}/docs",
    f"{settings.API_PREFIX}/redoc",
    f"{settings.API_PREFIX}/docs/oauth2-redirect",
}


class AuthMiddleware(BaseHTTPMiddleware):

    @staticmethod
    async def _verify(request: Request, token_type: TokenType) -> JSONResponse | None:
        try:
            header = TokenHeader.get(token_type)
            token = Token.extract(request.headers.get(header))
            if not token:
                return TokenException.invalid_response(detail=AuthError.INVALID_HEADER.format(token_type))
            if token_type == TokenType.ACCESS:
                await Token.verify(token, token_type, await get_redis(request))
            elif token_type == TokenType.REFRESH:
                new_token = await Token.refresh(token, await get_redis(request))
                setattr(request.state, "new_token", new_token)
        except ExpiredSignatureError:
            return TokenException.expire_response()
        except (InvalidTokenError, ValidationError):
            return TokenException.invalid_response()
        except HTTPException as exc:
            return CommonException.error_response(detail=exc.detail, status_code=exc.status_code)
        except Exception as exc:
            return CommonException.error_response(detail=str(exc))

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in _WHITE_URL:
            return await call_next(request)

        endpoint = request.scope.get("endpoint")
        if endpoint and getattr(endpoint, "_skip_auth", False):
            return await call_next(request)

        # verify access token
        error_response = await self._verify(request=request, token_type=TokenType.ACCESS)
        if error_response:
            if error_response.status_code != status.HTTP_401_UNAUTHORIZED:
                return error_response
            # try refresh access token
            error_response = await self._verify(request=request, token_type=TokenType.REFRESH)
            if error_response:
                return error_response

        response = await call_next(request)
        if new_token := getattr(request.state, "new_token", None):
            header = TokenHeader.get(TokenType.ACCESS, is_new=True)
            response.headers[header] = new_token
        return response
