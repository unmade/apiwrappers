from typing import Awaitable, Dict, Generic, TypeVar, Union, overload

from apiwrappers import AsyncDriver, AsyncResponse, Driver, Method, Request, Response

DT = TypeVar("DT", Driver, AsyncDriver)


class APIWrapper(Generic[DT]):
    host: str
    driver: DT

    def __init__(self, host: str, driver: DT):
        ...

    @overload
    def get_hello_world(self: APIWrapper[Driver]) -> Response:
        ...

    @overload
    def get_hello_world(self: APIWrapper[AsyncDriver]) -> Awaitable[AsyncResponse]:
        ...

    @overload
    def echo_headers(self: APIWrapper[Driver], headers: Dict[str, str]) -> Response:
        ...

    @overload
    def echo_headers(self: APIWrapper[AsyncDriver], headers: Dict[str, str]) -> Awaitable[AsyncResponse]:
        ...
