from typing import (
    Awaitable,
    Dict,
    Generic,
    Iterable,
    Mapping,
    Tuple,
    TypeVar,
    Union,
    overload,
)

from apiwrappers import AsyncDriver, AsyncResponse, Driver, Method, Request, Response
from apiwrappers.typedefs import JSON, Data, QueryParams, Timeout
from apiwrappers.utils import NoValue

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

    @overload
    def timeout(self: APIWrapper[Driver], timeout: Union[Timeout, NoValue]) -> Response:
        ...

    @overload
    def timeout(self: APIWrapper[AsyncDriver], timeout: Union[Timeout, NoValue]) -> Awaitable[AsyncResponse]:
        ...

    @overload
    def verify_ssl(self: APIWrapper[Driver], verify_ssl: Union[bool, NoValue]) -> Response:
        ...

    @overload
    def verify_ssl(self: APIWrapper[AsyncDriver], verify_ssl: Union[bool, NoValue]) -> Awaitable[AsyncResponse]:
        ...

    @overload
    def exception(self: APIWrapper[Driver]) -> Response:
        ...

    @overload
    def exception(self: APIWrapper[AsyncDriver]) -> Awaitable[AsyncResponse]:
        ...
