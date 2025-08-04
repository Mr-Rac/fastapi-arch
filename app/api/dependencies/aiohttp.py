import logging
from typing import Optional

from aiohttp import ClientSession, web
from fastapi import Request


async def get_aiohttp(request: Request) -> ClientSession:
    return request.app.state.aiohttp_session


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
