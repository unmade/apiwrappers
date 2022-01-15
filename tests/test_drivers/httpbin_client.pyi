from __future__ import annotations

from typing import Awaitable, Generic, MutableMapping, Optional, TypeVar, overload

from apiwrappers import AsyncDriver, Driver, Response, Url
from apiwrappers.typedefs import Data, Files, Json, QueryParams, Timeout

T = TypeVar("T", Driver, AsyncDriver)

class HttpBin(Generic[T]):
    url: Url
    driver: T
    def __init__(self, host: str, driver: T): ...
    @overload
    def get(
        self: HttpBin[Driver], params: Optional[QueryParams] = None
    ) -> Response: ...
    @overload
    def get(
        self: HttpBin[AsyncDriver], params: Optional[QueryParams] = None
    ) -> Awaitable[Response]: ...
    @overload
    def post(
        self: HttpBin[Driver],
        data: Optional[Data] = None,
        files: Optional[Files] = None,
        json: Optional[Json] = None,
    ) -> Response: ...
    @overload
    def post(
        self: HttpBin[AsyncDriver],
        data: Optional[Data] = None,
        files: Optional[Files] = None,
        json: Optional[Json] = None,
    ) -> Awaitable[Response]: ...
    @overload
    def headers(
        self: HttpBin[Driver], headers: MutableMapping[str, str]
    ) -> Response: ...
    @overload
    def headers(
        self: HttpBin[AsyncDriver], headers: MutableMapping[str, str]
    ) -> Awaitable[Response]: ...
    @overload
    def response_headers(
        self: HttpBin[Driver], headers: MutableMapping[str, str]
    ) -> Response: ...
    @overload
    def response_headers(
        self: HttpBin[AsyncDriver], headers: MutableMapping[str, str]
    ) -> Awaitable[Response]: ...
    @overload
    def cookies(
        self: HttpBin[Driver], cookies: MutableMapping[str, str]
    ) -> Response: ...
    @overload
    def cookies(
        self: HttpBin[AsyncDriver], cookies: MutableMapping[str, str]
    ) -> Awaitable[Response]: ...
    @overload
    def set_cookie(self: HttpBin[Driver], name: str, value: str) -> Response: ...
    @overload
    def set_cookie(
        self: HttpBin[AsyncDriver], name: str, value: str
    ) -> Awaitable[Response]: ...
    @overload
    def delay(self: HttpBin[Driver], delay: int, timeout: Timeout) -> Response: ...
    @overload
    def delay(
        self: HttpBin[AsyncDriver], delay: int, timeout: Timeout
    ) -> Awaitable[Response]: ...
    @overload
    def html(self: HttpBin[Driver]) -> Response: ...
    @overload
    def html(self: HttpBin[AsyncDriver]) -> Awaitable[Response]: ...
    @overload
    def basic_auth(self: HttpBin[Driver], login: str, password: str) -> Response: ...
    @overload
    def basic_auth(
        self: HttpBin[AsyncDriver], login: str, password: str
    ) -> Awaitable[Response]: ...
    @overload
    def bearer_auth(self: HttpBin[Driver], token: str) -> Response: ...
    @overload
    def bearer_auth(self: HttpBin[AsyncDriver], token: str) -> Awaitable[Response]: ...
    @overload
    def complex_auth_flow(self: HttpBin[Driver], token: str) -> Response: ...
    @overload
    def complex_auth_flow(
        self: HttpBin[AsyncDriver], token: str
    ) -> Awaitable[Response]: ...
