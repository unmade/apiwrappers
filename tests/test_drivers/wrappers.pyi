from typing import (
    Awaitable,
    Dict,
    Generic,
    Mapping,
    TypeVar,
    Union,
    overload,
)

from apiwrappers import AsyncDriver, Driver, Response
from apiwrappers.structures import NoValue
from apiwrappers.typedefs import JSON, Data, QueryParams, Timeout

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
    def get_hello_world(self: APIWrapper[AsyncDriver]) -> Awaitable[Response]:
        ...

    @overload
    def echo_headers(self: APIWrapper[Driver], headers: Dict[str, str]) -> Response:
        ...

    @overload
    def echo_headers(self: APIWrapper[AsyncDriver], headers: Dict[str, str]) -> Awaitable[Response]:
        ...

    @overload
    def echo_query_params(self: APIWrapper[Driver], query_params: QueryParams) -> Response:
        ...

    @overload
    def echo_query_params(self: APIWrapper[AsyncDriver], query_params: QueryParams) -> Awaitable[Response]:
        ...

    @overload
    def echo_cookies(self: APIWrapper[Driver], cookies: Mapping[str, str]) -> Response:
        ...

    @overload
    def echo_cookies(self: APIWrapper[AsyncDriver], cookies: Mapping[str, str]) -> Awaitable[Response]:
        ...

    @overload
    def send_data(self: APIWrapper[Driver], payload: Data) -> Response:
        ...

    @overload
    def send_data(self: APIWrapper[AsyncDriver], payload: Data) -> Awaitable[Response]:
        ...

    @overload
    def send_json(self: APIWrapper[Driver], payload: JSON) -> Response:
        ...

    @overload
    def send_json(self: APIWrapper[AsyncDriver], payload: JSON) -> Awaitable[Response]:
        ...

    @overload
    def timeout(self: APIWrapper[Driver], timeout: Union[Timeout, NoValue]) -> Response:
        ...

    @overload
    def timeout(self: APIWrapper[AsyncDriver], timeout: Union[Timeout, NoValue]) -> Awaitable[Response]:
        ...

    @overload
    def verify_ssl(self: APIWrapper[Driver], verify_ssl: Union[bool, NoValue]) -> Response:
        ...

    @overload
    def verify_ssl(self: APIWrapper[AsyncDriver], verify_ssl: Union[bool, NoValue]) -> Awaitable[Response]:
        ...

    @overload
    def exception(self: APIWrapper[Driver]) -> Response:
        ...

    @overload
    def exception(self: APIWrapper[AsyncDriver]) -> Awaitable[Response]:
        ...

    @overload
    def middleware(self: APIWrapper[Driver]) -> Response:
        ...

    @overload
    def middleware(self: APIWrapper[AsyncDriver]) -> Awaitable[Response]:
        ...

    @overload
    def basic_auth(self: APIWrapper[Driver]) -> Response:
        ...

    @overload
    def basic_auth(self: APIWrapper[AsyncDriver]) -> Awaitable[Response]:
        ...

    @overload
    def token_auth(self: APIWrapper[Driver]) -> Response:
        ...

    @overload
    def token_auth(self: APIWrapper[AsyncDriver]) -> Awaitable[Response]:
        ...

    @overload
    def complex_auth_flow(self: APIWrapper[Driver]) -> Response:
        ...

    @overload
    def complex_auth_flow(self: APIWrapper[AsyncDriver]) -> Awaitable[Response]:
        ...
