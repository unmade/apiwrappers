from http.cookies import SimpleCookie
from typing import Iterable, List, Tuple

import aiohttp

from apiwrappers import utils
from apiwrappers.entities import AsyncResponse, QueryParams, Request, Timeout
from apiwrappers.structures import CaseInsensitiveDict

DEFAULT_TIMEOUT = 5 * 60  # 5 minutes


class AioHttpDriver:
    def __init__(self, timeout: Timeout = DEFAULT_TIMEOUT):
        self.timeout = timeout

    async def fetch(self, request: Request, timeout: Timeout = None) -> AsyncResponse:
        async with aiohttp.ClientSession() as session:
            response = await session.request(
                request.method.value,
                utils.build_url(request.host, request.path),
                headers=request.headers,
                cookies=request.cookies,
                params=self._prepare_query_params(request.query_params),
                data=request.data,
                json=request.json,
                timeout=self._prepare_timeout(timeout),
            )
            return AsyncResponse(
                status_code=int(response.status),
                url=str(response.url),
                headers=CaseInsensitiveDict(response.headers),
                cookies=SimpleCookie(response.cookies),
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

    def _prepare_timeout(self, timeout: Timeout) -> Timeout:
        return timeout or self.timeout
