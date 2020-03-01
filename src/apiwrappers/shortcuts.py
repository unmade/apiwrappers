# pylint: disable=too-many-arguments

import asyncio
from typing import Awaitable, Callable, Optional, Type, TypeVar, Union, overload

from apiwrappers import utils
from apiwrappers.entities import Request, Response
from apiwrappers.protocols import AsyncDriver, Driver
from apiwrappers.structures import NoValue
from apiwrappers.typedefs import Timeout

T = TypeVar("T")

_Timeout = Union[Timeout, NoValue]

NO_VALUE = NoValue()


@overload
def fetch(
    driver: Driver,
    request: Request,
    timeout: _Timeout = NoValue(),
    model: None = None,
    source: Optional[str] = None,
) -> Response:
    ...


@overload
def fetch(
    driver: AsyncDriver,
    request: Request,
    timeout: _Timeout = NoValue(),
    model: None = None,
    source: Optional[str] = None,
) -> Awaitable[Response]:
    ...


@overload
def fetch(
    driver: Driver,
    request: Request,
    timeout: _Timeout = NoValue(),
    model: Union[Callable[..., T], Type[T]] = None,
    source: Optional[str] = None,
) -> T:
    ...


@overload
def fetch(
    driver: AsyncDriver,
    request: Request,
    timeout: _Timeout = NoValue(),
    model: Union[Callable[..., T], Type[T]] = None,
    source: Optional[str] = None,
) -> Awaitable[T]:
    ...


def fetch(
    driver: Union[Driver, AsyncDriver],
    request: Request,
    timeout: _Timeout = NO_VALUE,
    model: Optional[Union[Callable[..., T], Type[T]]] = None,
    source: Optional[str] = None,
) -> Union[Response, Awaitable[Response], T, Awaitable[T]]:
    """
    Makes a request and returns response from server.

    This is shortcut function for making requests. Prefer this over
    :py:meth:`Driver.fetch() <apiwrappers.Driver.fetch>` and
    :py:meth:`AsyncDriver.fetch() <apiwrappers.AsyncDriver.fetch>`.
    It also has extended behaviour and can parse JSON if ``model`` arg provided.

    Args:
        driver: driver that actually makes a request.
        request: request object.
        timeout: how many seconds to wait for the server to send data before giving up.
            If set to ``None`` waits infinitely. If provided, will take precedence over
            the ``driver.timeout``.
        model: parser for a json response. This can be either type, e.g. List[int], or
            a callable that accepts json.
        source: name of the key in the json, which value will be passed to the model.
            You may use dotted notation to traverse keys, e.g. ``key1.key2``.

    Returns:
        * **Response** if regular driver is provided and ``model`` is not.
        * **Awaitable[Response]** if asynchronous driver is provided, ``model`` is not.
        * **T** if regular driver and model is provided. The ``T`` corresponds to
          ``model`` type.
        * **Awaitable[T]** if asynchronous driver and model is provided. The ``T``
          corresponds to ``model`` type.

    Raises:
        Timeout: the request timed out.
        ssl.SSLError: An SSL error occurred.
        ConnectionFailed: a connection error occurred.
        DriverError: in case of any other error in driver underlying library.

    Simple Usage::

        >>> from apiwrappers import Method, Request, fetch, make_driver
        >>> driver = make_driver("requests")
        >>> request = Request(Method.GET, "https://example.org", "/")
        >>> response = fetch(driver, request)
        <Response [200]>

    To use it in asynchronous code just use proper driver and don't forget to await::

        >>> from apiwrappers import Method, Request, fetch, make_driver
        >>> driver = make_driver("aiohttp")
        >>> request = Request(Method.GET, "https://example.org", "/")
        >>> response = await fetch(driver, request)
        <Response [200]>

    If you provide ``model`` argument the JSON response will be parsed::

        >>> from dataclasses import dataclass
        >>> from typing import List
        >>> from apiwrappers import Method, Request, fetch, make_driver
        >>> @dataclass
        ... class Repo:
        ...     name: str
        >>> driver = make_driver("requests")
        >>> Request(
        ...     Method.GET,
        ...     "https://api.github.com",
        ...     "/users/unmade/repos",
        ... )
        >>> fetch(driver, request, model=List[Repo])
        [Repo(name='am-date-picker'), ...]
    """
    if asyncio.iscoroutinefunction(driver.fetch):

        async def wrapper():
            resp = await driver.fetch(request, timeout=timeout)
            if model is None:
                return resp
            return utils.fromjson(model, utils.getitem(resp.json(), source))

    else:

        def wrapper():
            resp = driver.fetch(request, timeout=timeout)
            if model is None:
                return resp
            return utils.fromjson(model, utils.getitem(resp.json(), source))

    return wrapper()  # type: ignore
