import importlib
from typing import Tuple, Type, Union, overload

from apiwrappers.compat import Literal
from apiwrappers.protocols import AsyncDriver, AsyncMiddleware, Driver, Middleware
from apiwrappers.typedefs import Timeout
from apiwrappers.utils import NoValue

DRIVER_MAP = {
    "requests": ("apiwrappers.drivers.requests", "RequestsDriver"),
    "aiohttp": ("apiwrappers.drivers.aiohttp", "AioHttpDriver"),
}
DRIVERS = Literal["requests", "aiohttp"]


@overload
def make_driver(
    driver_type: Literal["requests"],
    *middleware: Type[Middleware],
    timeout: Union[NoValue, Timeout] = NoValue(),
) -> Driver:
    ...


@overload
def make_driver(
    driver_type: Literal["aiohttp"],
    *middleware: Type[AsyncMiddleware],
    timeout: Union[NoValue, Timeout] = NoValue(),
) -> AsyncDriver:
    ...


# Fallback overload for when the user isn't using literal types
@overload
def make_driver(
    driver_type: str,
    *middleware: Type[AsyncMiddleware],
    timeout: Union[NoValue, Timeout] = NoValue(),
) -> Union[Driver, AsyncDriver]:
    ...


def make_driver(driver_type, *middleware, timeout=NoValue(), verify_ssl=NoValue()):
    module_name, driver_name = _get_import_params(driver_type)
    module = importlib.import_module(module_name)
    driver = getattr(module, driver_name)
    return driver(*middleware, timeout, verify_ssl)


def _get_import_params(driver_type: str) -> Tuple[str, str]:
    try:
        return DRIVER_MAP[driver_type]
    except KeyError as exc:
        drivers = ", ".join(DRIVER_MAP.keys())
        msg = f"No such driver: {driver_type}. Possible drivers are: {drivers}"
        raise ValueError(msg) from exc
