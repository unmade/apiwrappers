# pylint: disable=no-self-use

import aiohttp

from apiwrappers import utils
from apiwrappers.entities import AsyncResponse, Request


class AioHttpDriver:
    async def fetch(self, request: Request) -> AsyncResponse:
        async with aiohttp.ClientSession() as session:
            response = await session.request(
                request.method.value,
                utils.build_url(request.host, request.path),
                data=request.data,
                json=request.json,
                ssl=request.verify_ssl,
                timeout=aiohttp.client.ClientTimeout(total=request.timeout),
            )
            return AsyncResponse(
                status_code=int(response.status),
                url=str(response.url),
                content=await response.read(),
                text=response.text,
                json=response.json,
            )
