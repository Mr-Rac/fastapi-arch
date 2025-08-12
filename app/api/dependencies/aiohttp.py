import logging
from typing import Optional

from aiohttp import ClientSession, web
from fastapi import Request, HTTPException, status

from app.exception import ERR


async def get_aiohttp(request: Request) -> ClientSession:
    session: ClientSession | None = getattr(request.app.state, "aiohttp_session", None)
    if not session:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=ERR.DEPENDENCY_AIOHTTP_INVALID)
    return session


async def post(
        session: ClientSession,
        url: str,
        data: Optional[dict] = None,
        headers: Optional[dict] = None,
) -> web.Response:
    async with session.post(url, json=data, headers=headers) as resp:
        logging.warning(
            f"\n请求url: {url}"
            f"\npayload: {data}"
            f"\nresponse: {await resp.json()}"
        )
        return await resp.json()
