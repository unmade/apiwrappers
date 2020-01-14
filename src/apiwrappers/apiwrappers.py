import asyncio
from typing import Awaitable, Callable, Generic, Optional, Type, TypeVar, overload

from apiwrappers.entities import Request
from apiwrappers.protocols import AsyncDriver, Driver, WrapperLike

T = TypeVar("T")
RequestFactory = Callable[..., Request]
RF = TypeVar("RF", bound=RequestFactory)


class Fetch(Generic[T]):
    def __init__(self, factory: Callable[..., T]):
        self.factory: Callable[..., T] = factory
        self.request_factory: Optional[RequestFactory] = None

    @overload
    def __get__(
        self, obj: WrapperLike[Driver], objtype: Type[WrapperLike[Driver]]
    ) -> Callable[..., T]:
        ...

    @overload
    def __get__(
        self, obj: WrapperLike[AsyncDriver], objtype: Type[WrapperLike[AsyncDriver]]
    ) -> Callable[..., Awaitable[T]]:
        ...

    def __get__(self, obj, objtype):
        def wrapper(*args, **kwargs):
            request = self.request_factory(obj, *args, **kwargs)
            return self.response(obj.driver, request)

        return wrapper

    def request(self, request_factory: RF) -> RF:
        self.request_factory = request_factory
        return request_factory

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
