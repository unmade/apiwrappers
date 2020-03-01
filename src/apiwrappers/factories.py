from __future__ import annotations

import importlib
from typing import Tuple, Type, Union, overload

from apiwrappers.compat import Literal
from apiwrappers.protocols import AsyncDriver, AsyncMiddleware, Driver, Middleware
from apiwrappers.typedefs import ClientCert, Timeout, Verify

DEFAULT_TIMEOUT = 5 * 60  # 5 minutes
DRIVER_MAP = {
    "requests": ("apiwrappers.drivers.requests", "RequestsDriver"),
    "aiohttp": ("apiwrappers.drivers.aiohttp", "AioHttpDriver"),
}


@overload
def make_driver(
    driver_type: Literal["requests"],
    *middleware: Type[Middleware],
    timeout: Timeout = DEFAULT_TIMEOUT,
    verify: Verify = True,
    cert: ClientCert = None,
) -> Driver:
    ...


@overload
def make_driver(
    driver_type: Literal["aiohttp"],
    *middleware: Type[AsyncMiddleware],
    timeout: Timeout = DEFAULT_TIMEOUT,
    verify: Verify = True,
    cert: ClientCert = None,
) -> AsyncDriver:
    ...


# Fallback overload for when the user isn't using literal types
@overload
def make_driver(
    driver_type: str,
    *middleware: Union[Type[Middleware], Type[AsyncMiddleware]],
    timeout: Timeout = DEFAULT_TIMEOUT,
    verify: Verify = True,
    cert: ClientCert = None,
) -> Union[Driver, AsyncDriver]:
    ...


def make_driver(
    driver_type: str,
    *middleware: Union[Type[Middleware], Type[AsyncMiddleware]],
    timeout: Timeout = DEFAULT_TIMEOUT,
    verify: Verify = True,
    cert: ClientCert = None,
) -> Union[Driver, AsyncDriver]:
    """
    Creates driver instance and returns it

    This is a factory function to ease driver instantiation. That way you can abstract
    from specific driver class - no need to import it, no need to know how the class
    is called.

    Args:
        driver_type: specifies what kind of driver to create. Valid choices are
            ``request`` and ``aiohttp``.
        *middleware: :ref:`middleware <middleware>` to apply to driver. Dependant on
            ``driver_type`` it should be of one kind - either ``Type[Middleware]``
            for regular drivers and ``Type[AsyncMiddleware]`` for asynchronous ones.
        timeout: how many seconds to wait for the server to send data before giving up.
            If set to ``None`` waits infinitely.
        verify: Either a boolean, in which case it controls whether to verify the
            server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use.
        cert: Either a path to SSL client cert file (.pem) or a ('cert', 'key') tuple.

    Returns:
        * **Driver** if ``driver_type`` is ``requests``.
        * **AsyncDriver** if ``driver_type`` is ``aiohttp``.

    Raises:
        ValueError: if unknown driver type specified

    Usage::

        >>> from apiwrappers import make_driver
        >>> make_driver("requests")
        RequestsDriver(timeout=300, verify=True)
    """
    module_name, driver_name = _get_import_params(driver_type)
    module = importlib.import_module(module_name)
    driver_class = getattr(module, driver_name)
    driver = driver_class(*middleware, timeout=timeout, verify=verify, cert=cert)
    return driver  # type: ignore


def _get_import_params(driver_type: str) -> Tuple[str, str]:
    try:
        return DRIVER_MAP[driver_type]
    except KeyError as exc:
        drivers = ", ".join(DRIVER_MAP.keys())
        msg = f"No such driver: {driver_type}. Possible drivers are: {drivers}"
        raise ValueError(msg) from exc
