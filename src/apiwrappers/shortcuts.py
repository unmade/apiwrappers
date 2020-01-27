# pylint: disable=too-many-arguments

import asyncio
from typing import Awaitable, Optional, TypeVar, Union, overload

from apiwrappers import AsyncDriver, Driver, Request, Response, utils
from apiwrappers.structures import NoValue
from apiwrappers.typedefs import Timeout

T = TypeVar("T")


@overload
def fetch(
    driver: Driver,
    request: Request,
    timeout: Union[Timeout, NoValue] = NoValue(),
    verify_ssl: Union[bool, NoValue] = NoValue(),
    model: None = None,
    source: Optional[str] = None,
) -> Response:
    ...


@overload
def fetch(
    driver: AsyncDriver,
    request: Request,
    timeout: Union[Timeout, NoValue] = NoValue(),
    verify_ssl: Union[bool, NoValue] = NoValue(),
    model: None = None,
    source: Optional[str] = None,
) -> Awaitable[Response]:
    ...


@overload
def fetch(
    driver: Driver,
    request: Request,
    timeout: Union[Timeout, NoValue] = NoValue(),
    verify_ssl: Union[bool, NoValue] = NoValue(),
    model: T = None,
    source: Optional[str] = None,
) -> T:
    ...


@overload
def fetch(
    driver: AsyncDriver,
    request: Request,
    timeout: Union[Timeout, NoValue] = NoValue(),
    verify_ssl: Union[bool, NoValue] = NoValue(),
    model: T = None,
    source: Optional[str] = None,
) -> Awaitable[T]:
    ...


def fetch(
    driver, request, timeout=NoValue(), verify_ssl=NoValue(), model=None, source=None
):
    if asyncio.iscoroutinefunction(driver.fetch):

        async def wrapper():
            resp = await driver.fetch(request, timeout=timeout, verify_ssl=verify_ssl)
            if model is None:
                return resp
            return utils.fromjson(model, utils.getitem(resp.json(), source))

    else:

        def wrapper():
            resp = driver.fetch(request, timeout=timeout, verify_ssl=verify_ssl)
            if model is None:
                return resp
            return utils.fromjson(model, utils.getitem(resp.json(), source))

    return wrapper()
