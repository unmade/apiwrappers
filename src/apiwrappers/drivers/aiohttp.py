import asyncio
from http.cookies import SimpleCookie
from typing import Iterable, List, Tuple, Union

import aiohttp

from apiwrappers import exceptions, utils
from apiwrappers.entities import AsyncResponse, Request
from apiwrappers.structures import CaseInsensitiveDict
from apiwrappers.typedefs import QueryParams, Timeout
from apiwrappers.utils import NoValue

DEFAULT_TIMEOUT = 5 * 60  # 5 minutes


class AioHttpDriver:
    def __init__(self, timeout: Timeout = DEFAULT_TIMEOUT, verify_ssl: bool = True):
        self.timeout = timeout
        self.verify_ssl = verify_ssl

    async def fetch(
        self,
        request: Request,
        timeout: Union[Timeout, NoValue] = NoValue(),
        verify_ssl: Union[bool, NoValue] = NoValue(),
    ) -> AsyncResponse:
        async with aiohttp.ClientSession() as session:
            try:
                response = await session.request(
                    request.method.value,
                    utils.build_url(request.host, request.path),
                    headers=request.headers,
                    cookies=request.cookies,
                    params=self._prepare_query_params(request.query_params),
                    data=request.data,
                    json=request.json,
                    timeout=self._prepare_timeout(timeout),
                    ssl=self._prepare_ssl(verify_ssl),
                )
            except asyncio.TimeoutError as exc:
                raise exceptions.Timeout from exc
            except aiohttp.ClientConnectionError as exc:
                raise exceptions.ConnectionFailed from exc
            except aiohttp.ClientError as exc:
                raise exceptions.DriverError from exc

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

    def _prepare_timeout(self, timeout: Union[Timeout, NoValue]) -> Timeout:
        if isinstance(timeout, NoValue):
            return self.timeout
        return timeout

    def _prepare_ssl(self, verify_ssl: Union[bool, NoValue]) -> bool:
        if isinstance(verify_ssl, NoValue):
            return self.verify_ssl
        return verify_ssl
