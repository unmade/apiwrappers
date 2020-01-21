from __future__ import annotations

from typing import Awaitable, List, Type, TypeVar, Union

from apiwrappers.compat import Protocol
from apiwrappers.entities import Request, Response
from apiwrappers.structures import NoValue
from apiwrappers.typedefs import Timeout

T = TypeVar("T", "Driver", "AsyncDriver")


class WrapperLike(Protocol[T]):
    driver: T


class Driver(Protocol):
    timeout: Timeout
    verify_ssl: bool
    middleware: List[Type[Middleware]]

    def fetch(
        self,
        request: Request,
        timeout: Union[Timeout, NoValue] = NoValue(),
        verify_ssl: Union[bool, NoValue] = NoValue(),
    ) -> Response:
        ...


class AsyncDriver(Protocol):
    timeout: Timeout
    verify_ssl: bool
    middleware: List[Type[AsyncMiddleware]]

    async def fetch(
        self,
        request: Request,
        timeout: Union[Timeout, NoValue] = NoValue(),
        verify_ssl: Union[bool, NoValue] = NoValue(),
    ) -> Response:
        ...


class Middleware(Protocol):
    handler: Handler

    def __call__(
        self,
        request: Request,
        timeout: Union[Timeout, NoValue] = NoValue(),
        verify_ssl: Union[bool, NoValue] = NoValue(),
    ) -> Response:
        ...


class AsyncMiddleware(Protocol):
    handler: Handler

    def __call__(
        self,
        request: Request,
        timeout: Union[Timeout, NoValue] = NoValue(),
        verify_ssl: Union[bool, NoValue] = NoValue(),
    ) -> Awaitable[Response]:
        ...


class Handler(Protocol):
    def __call__(
        self,
        request: Request,
        timeout: Union[Timeout, NoValue] = NoValue(),
        verify_ssl: Union[bool, NoValue] = NoValue(),
    ) -> Response:
        ...


class AsyncHandler(Protocol):
    def __call__(
        self,
        request: Request,
        timeout: Union[Timeout, NoValue] = NoValue(),
        verify_ssl: Union[bool, NoValue] = NoValue(),
    ) -> Awaitable[Response]:
        ...
