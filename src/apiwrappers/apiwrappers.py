import asyncio
from typing import Awaitable, Callable, Generic, TypeVar, overload

from apiwrappers.entities import Request
from apiwrappers.protocols import AsyncDriver, Driver

T = TypeVar("T")


class Fetch(Generic[T]):
    def __init__(self, factory: Callable[..., T]):
        self.factory: Callable[..., T] = factory

    @overload
    def response(self, driver: Driver, request: Request) -> T:
        # pylint: disable=no-self-use
        ...

    @overload
    def response(self, driver: AsyncDriver, request: Request) -> Awaitable[T]:
        # pylint: disable=no-self-use
        ...

    def response(self, driver, request):
        if not asyncio.iscoroutinefunction(driver.fetch):
            resp = driver.fetch(request)
            return self.factory(resp.json())

        async def async_response():
            resp = await driver.fetch(request)
            return self.factory(resp.json())

        return async_response()
