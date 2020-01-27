from typing import Awaitable, Callable, Generic, Optional, Type, TypeVar, overload

from apiwrappers.entities import Request
from apiwrappers.protocols import AsyncDriver, Driver, WrapperLike
from apiwrappers.shortcuts import fetch

T = TypeVar("T")
RequestFactory = Callable[..., Request]
RF = TypeVar("RF", bound=RequestFactory)


class Fetch(Generic[T]):
    def __init__(self, model: Callable[..., T], source: Optional[str] = None):
        self.model: Callable[..., T] = model
        self.source = source
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
            return fetch(obj.driver, request, model=self.model, source=self.source)

        return wrapper

    def request(self, request_factory: RF) -> RF:
        self.request_factory = request_factory
        return request_factory
