from typing import Awaitable, Dict, Generic, Iterable, Mapping, Tuple, TypeVar, Union, overload

from apiwrappers import AsyncDriver, AsyncResponse, Driver, Method, Request, Response
from apiwrappers.entities import Data, JSON, QueryParams

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

    @overload
    def echo_query_params(self: APIWrapper[Driver], query_params: QueryParams) -> Response:
        ...

    @overload
    def echo_query_params(self: APIWrapper[AsyncDriver], query_params: QueryParams) -> Awaitable[AsyncResponse]:
        ...

    @overload
    def echo_cookies(self: APIWrapper[Driver], cookies: Mapping[str, str]) -> Response:
        ...

    @overload
    def echo_cookies(self: APIWrapper[AsyncDriver], cookies: Mapping[str, str]) -> Awaitable[AsyncResponse]:
        ...

    @overload
    def send_data(self: APIWrapper[Driver], payload: Data) -> Response:
        ...

    @overload
    def send_data(self: APIWrapper[AsyncDriver], payload: Data) -> Awaitable[AsyncResponse]:
        ...

    @overload
    def send_json(self: APIWrapper[Driver], payload: JSON) -> Response:
        ...

    @overload
    def send_json(self: APIWrapper[AsyncDriver], payload: JSON) -> Awaitable[AsyncResponse]:
        ...
