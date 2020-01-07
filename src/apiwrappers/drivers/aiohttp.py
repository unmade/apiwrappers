# pylint: disable=no-self-use

from typing import Iterable, List, Tuple

import aiohttp

from apiwrappers import utils
from apiwrappers.entities import AsyncResponse, QueryParams, Request
from apiwrappers.structures import CaseInsensitiveDict


class AioHttpDriver:
    async def fetch(self, request: Request) -> AsyncResponse:
        async with aiohttp.ClientSession() as session:
            response = await session.request(
                request.method.value,
                utils.build_url(request.host, request.path),
                headers=request.headers,
                params=self._prepare_query_params(request.query_params),
                data=request.data,
                json=request.json,
                ssl=request.verify_ssl,
                timeout=aiohttp.client.ClientTimeout(total=request.timeout),
            )
            return AsyncResponse(
                status_code=int(response.status),
                url=str(response.url),
                headers=CaseInsensitiveDict(response.headers),
                content=await response.read(),
                text=response.text,
                json=response.json,
            )

    @staticmethod
    def _prepare_query_params(params: QueryParams) -> Tuple[Tuple[str, str], ...]:
        query_params: List[Tuple[str, str]] = []
        for key, value in params.items():
            if isinstance(value, Iterable) and not isinstance(value, str):
                query_params.extend([(key, subvalue) for subvalue in value])
            elif value is None:
                continue
            else:
                query_params.append((key, value))
        return tuple(query_params)
