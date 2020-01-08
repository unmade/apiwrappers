from typing import Awaitable, Dict, Generic, Mapping, TypeVar, Union, overload

from apiwrappers import AsyncDriver, AsyncResponse, Driver, Method, Request, Response
from apiwrappers.entities import QueryParams

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
    def send_data_as_dict(self: APIWrapper[Driver]) -> Response:
        ...

    @overload
    def send_data_as_dict(self: APIWrapper[AsyncDriver]) -> Awaitable[AsyncResponse]:
        ...

    # @overload
    # def send_data_as_tuples(self: APIWrapper[Driver]) -> Response:
    #     ...

    # @overload
    # def send_data_as_tuples(self: APIWrapper[AsyncDriver]) -> Awaitable[AsyncResponse]:
    #     ...
