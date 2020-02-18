from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, TypeVar, Union

from apiwrappers.compat import Protocol
from apiwrappers.entities import Request, Response
from apiwrappers.structures import NoValue
from apiwrappers.typedefs import Timeout

if TYPE_CHECKING:
    # pylint: disable=cyclic-import
    from apiwrappers.middleware.chain import MiddlewareChain

T = TypeVar("T", "Driver", "AsyncDriver")


class WrapperLike(Protocol[T]):
    driver: T


class Driver(Protocol):
    """
    Protocol describing regular synchronous driver.

    Attributes:
        middleware: list of :ref:`middleware <middleware>` to be run on every request.
        timeout: how many seconds to wait for the server to send data before giving up.
            If set to ``None`` should wait infinitely.
        verify_ssl: whether to verify the server's TLS certificate or not.
    """

    middleware: MiddlewareChain
    timeout: Timeout
    verify_ssl: bool

    def fetch(
        self,
        request: Request,
        timeout: Union[Timeout, NoValue] = NoValue(),
        verify_ssl: Union[bool, NoValue] = NoValue(),
    ) -> Response:
        """
        Makes actual request and returns response from the server.

        Args:
            request: a request object with data to send to server.
            timeout: how many seconds to wait for the server to send data before
                giving up. If set to ``None`` waits infinitely. If provided, will take
                precedence over the :py:attr:`Driver.timeout`.
            verify_ssl: whether to verify the server's TLS certificate or not.
                If provided will take precedence over the :py:attr:`Driver.verify_ssl`.

        Returns: response from the server.

        Raises:
            Timeout: The request timed out.
            ConnectionFailed: A Connection error occurred.
            DriverError: In case of any other error in driver underlying library.
        """
        ...


class AsyncDriver(Protocol):
    """
    Protocol describing asynchronous driver.

    Attributes:
        middleware: list of :ref:`middleware <middleware>` to be run on every request.
        timeout: how many seconds to wait for the server to send data before giving up.
            If set to ``None`` should wait infinitely.
        verify_ssl: whether to verify the server's TLS certificate or not.
    """

    middleware: "MiddlewareChain"
    timeout: Timeout
    verify_ssl: bool

    async def fetch(
        self,
        request: Request,
        timeout: Union[Timeout, NoValue] = NoValue(),
        verify_ssl: Union[bool, NoValue] = NoValue(),
    ) -> Response:
        """
        Makes actual request and returns response from the server.

        Args:
            request: a request object with data to send to server.
            timeout: how many seconds to wait for the server to send data before
                giving up. If set to ``None`` waits infinitely. If provided, will take
                precedence over the :py:attr:`AsyncDriver.timeout`.
            verify_ssl: whether to verify the server's TLS certificate or not.
                If provided will take precedence over the
                :py:attr:`AsyncDriver.verify_ssl`.

        Returns: response from the server.

        Raises:
            Timeout: the request timed out.
            ConnectionFailed: a connection error occurred.
            DriverError: in case of any other error in driver underlying library.
        """
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
