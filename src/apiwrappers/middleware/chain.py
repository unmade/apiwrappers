from __future__ import annotations

import asyncio
import functools
from typing import Any, Callable, Iterable, List, Type, TypeVar, Union, cast, overload

from apiwrappers.protocols import AsyncDriver, AsyncMiddleware, Driver, Middleware

FuncType = Callable[..., Any]
FT = TypeVar("FT", bound=FuncType)

AnyMiddleware = TypeVar("AnyMiddleware", Type[Middleware], Type[AsyncMiddleware])
AnyMiddlewareList = Union[List[Type[Middleware]], List[Type[AsyncMiddleware]]]


class MiddlewareChain:
    def __init__(self, *middleware: AnyMiddleware):
        self.middleware: AnyMiddlewareList = list(middleware)

    @overload
    def __get__(self, obj: Driver, objtype: Type[Driver]) -> List[Type[Middleware]]:
        ...

    @overload
    def __get__(
        self, obj: AsyncDriver, objtype: Type[AsyncDriver]
    ) -> List[Type[AsyncMiddleware]]:
        ...

    @overload
    def __get__(self, obj: None, objtype: Type[Driver]) -> List[Type[Middleware]]:
        ...

    @overload
    def __get__(
        self, obj: None, objtype: Type[AsyncDriver]
    ) -> List[Type[AsyncMiddleware]]:
        ...

    def __get__(self, obj, objtype):
        if obj is None:
            return self.middleware
        try:
            return getattr(obj, "_middleware")
        except AttributeError:
            self.__set__(obj, self.middleware[:])
            return getattr(obj, "_middleware")

    @overload
    def __set__(self, obj: Driver, middleware: Iterable[Type[Middleware]]) -> None:
        ...

    @overload
    def __set__(
        self, obj: AsyncDriver, middleware: Iterable[Type[AsyncMiddleware]]
    ) -> None:
        ...

    def __set__(self, obj: Union[Driver, AsyncDriver], middleware) -> None:
        new_middleware = list(middleware)
        defaults = [item for item in self.middleware if item not in new_middleware]
        new_middleware = defaults + new_middleware
        setattr(obj, "_middleware", new_middleware)

    @staticmethod
    def wrap(func: FT) -> FT:
        if asyncio.iscoroutinefunction(func):

            async def wrapper(*args, **kwargs):
                instance = args[0]
                handler = functools.partial(func, instance)
                for middleware in reversed(instance.middleware):
                    handler = middleware(handler)
                return await handler(*args[1:], **kwargs)

        else:

            def wrapper(*args, **kwargs):
                instance = args[0]
                handler = functools.partial(func, instance)
                for middleware in reversed(instance.middleware):
                    handler = middleware(handler)
                return handler(*args[1:], **kwargs)

        return cast(FT, functools.wraps(func)(wrapper))
