from __future__ import annotations

import asyncio
import ssl
from http.cookies import SimpleCookie
from ssl import SSLContext
from typing import Iterable, List, Optional, Tuple, Type, Union, cast

import aiohttp
from aiohttp import FormData

from apiwrappers import exceptions, utils
from apiwrappers.entities import Request, Response
from apiwrappers.middleware import MiddlewareChain
from apiwrappers.middleware.auth import Authentication
from apiwrappers.protocols import AsyncMiddleware
from apiwrappers.structures import CaseInsensitiveDict, NoValue
from apiwrappers.typedefs import ClientCert, Data, QueryParams, Timeout, Verify

DEFAULT_TIMEOUT = 5 * 60  # 5 minutes


class AioHttpDriver:
    middleware = MiddlewareChain(Authentication)

    def __init__(
        self,
        *middleware: Type[AsyncMiddleware],
        timeout: Timeout = DEFAULT_TIMEOUT,
        verify: Verify = True,
        cert: ClientCert = None,
    ):
        self.middleware = middleware
        self.timeout = timeout
        self.verify = verify
        self.cert = cert

    def __repr__(self) -> str:
        middleware = [m.__name__ for m in self.middleware]
        if middleware:
            middleware.append("")
        return (
            f"{self.__class__.__name__}("
            f"{', '.join(middleware)}"
            f"timeout={self.timeout}, "
            f"verify={self.verify}"
            ")"
        )

    def __str__(self) -> str:
        return "<AsyncDriver 'aiohttp'>"

    @middleware.wrap
    async def fetch(
        self, request: Request, timeout: Union[Timeout, NoValue] = NoValue(),
    ) -> Response:
        async with aiohttp.ClientSession() as session:
            try:
                response = await session.request(
                    request.method.value,
                    utils.build_url(request.host, request.path),
                    headers=request.headers,
                    cookies=request.cookies,
                    params=self._prepare_query_params(request.query_params),
                    data=self._prepare_data(request),
                    json=request.json,
                    timeout=self._prepare_timeout(timeout),
                    ssl=self._prepare_ssl(),
                )
            except asyncio.TimeoutError as exc:
                raise exceptions.Timeout from exc
            except aiohttp.ClientConnectionError as exc:
                raise exceptions.ConnectionFailed from exc
            except aiohttp.ClientError as exc:
                raise exceptions.DriverError from exc

            return Response(
                request=request,
                status_code=int(response.status),
                url=str(response.url),
                headers=CaseInsensitiveDict(response.headers),
                cookies=SimpleCookie(response.cookies),
                content=await response.read(),
                encoding=response.get_encoding(),
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

    @staticmethod
    def _prepare_data(request: Request) -> Optional[Union[Data, FormData]]:
        if request.data is not None:
            return request.data
        if request.files is not None:
            data = FormData()
            for name, value in request.files.items():
                filename, content_type = None, None
                if isinstance(value, tuple):
                    if len(value) == 2:
                        filename, content = value  # type: ignore
                    else:
                        filename, content, content_type = value  # type: ignore
                else:
                    content = value
                data.add_field(
                    name, content, filename=filename, content_type=content_type,
                )
            return data
        return None

    def _prepare_ssl(self) -> SSLContext:
        if self.verify is True:
            context = ssl.create_default_context()
        elif self.verify is False:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        else:
            try:
                context = ssl.create_default_context(cafile=cast(str, self.verify))
            except FileNotFoundError as exc:
                msg = (
                    f"Could not find a suitable TLS CA certificate bundle, "
                    f"invalid path: {self.verify}"
                )
                raise FileNotFoundError(msg) from exc

        cert: Optional[str]
        key: Optional[str]
        if isinstance(self.cert, tuple):
            cert, key = self.cert
        else:
            cert, key = self.cert, None

        if cert is not None:
            try:
                context.load_cert_chain(cert, key)
            except FileNotFoundError as exc:
                msg = (
                    f"Could not find the TLS certificate file, "
                    f"invalid path: {self.cert}"
                )
                raise FileNotFoundError(msg) from exc

        return context
