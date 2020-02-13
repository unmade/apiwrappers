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
    """
    Protocol describing regular synchronous driver.

    Attributes:
        timeout (int, float, None): How many seconds to wait for the server to send
            data before giving up. If set to ``None`` should wait infinitely.
        verify_ssl (bool): Whether to verify the server's TLS certificate or not.
        middleware (List[Type[Middleware]]): List of :ref:`middleware <middleware>`
            to be run on every request
    """

    timeout: Timeout
    verify_ssl: bool
    middleware: List[Type[Middleware]]

    def fetch(
        self,
        request: Request,
        timeout: Union[Timeout, NoValue] = NoValue(),
        verify_ssl: Union[bool, NoValue] = NoValue(),
    ) -> Response:
        """
        Makes actual request and returns response from the server.

        Args:
            request (Request): A request object.
            timeout (int, float, None, apiwrappers.structures.NoValue): How many
                seconds to wait for the server to send data before giving up.
                If set to ``None`` waits infinitely. If provided, will take precedence
                over the ``Driver.timeout``.
            verify_ssl (bool, apiwrappers.structures.NoValue): Whether to verify the
                server's TLS certificate or not. If provided will take precedence over
                the ``Driver.verify_ssl``.

        Returns:
            (Response): Response from the server.

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
        timeout (int, float, None): How many seconds to wait for the server to send
            data before giving up. If set to ``None`` should wait infinitely.
        verify_ssl (bool): Whether to verify the server's TLS certificate or not.
        middleware (List[Type[AsyncMiddleware]]): List of :ref:`middleware <middleware>`
            to be run on every request.
    """

    timeout: Timeout
    verify_ssl: bool
    middleware: List[Type[AsyncMiddleware]]

    async def fetch(
        self,
        request: Request,
        timeout: Union[Timeout, NoValue] = NoValue(),
        verify_ssl: Union[bool, NoValue] = NoValue(),
    ) -> Response:
        """
        Makes actual request and returns response from the server.

        Args:
            request (Request): A request object.
            timeout (int, float, None, apiwrappers.structures.NoValue): How many
                seconds to wait for the server to send data before giving up.
                If set to ``None`` waits infinitely. If provided, will take precedence
                over the ``Driver.timeout``.
            verify_ssl (bool, apiwrappers.structures.NoValue): Whether to verify the
                server's TLS certificate or not. If provided will take precedence over
                the ``Driver.verify_ssl``.

        Returns:
            (Response): Response from the server.

        Raises:
            Timeout: The request timed out.
            ConnectionFailed: A Connection error occurred.
            DriverError: In case of any other error in driver underlying library.
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
