from __future__ import annotations

import asyncio
import functools
from typing import Any, Callable, Iterable, List, Type, TypeVar, Union, cast, overload

from apiwrappers.middleware.auth import Authorization
from apiwrappers.protocols import AsyncDriver, AsyncMiddleware, Driver, Middleware

FuncType = Callable[..., Any]
FT = TypeVar("FT", bound=FuncType)


class MiddlewareChain:
    def __init__(self):
        self.items = [Authorization]

    @overload
    def __get__(self, obj: Driver, objtype: Type[Driver]) -> List[Type[Middleware]]:
        ...

    @overload
    def __get__(
        self, obj: AsyncDriver, objtype: Type[AsyncDriver]
    ) -> List[Type[AsyncMiddleware]]:
        ...

    def __get__(self, obj, objtype):
        return getattr(obj, "_middleware", self.items[:])

    @overload
    def __set__(self, obj: Driver, middleware: Iterable[Type[Middleware]]) -> None:
        ...

    @overload
    def __set__(
        self, obj: AsyncDriver, middleware: Iterable[Type[AsyncMiddleware]]
    ) -> None:
        ...

    def __set__(self, obj: Union[Driver, AsyncDriver], middleware,) -> None:
        new_middleware = self.items + list(middleware)
        setattr(obj, "_middleware", new_middleware)
        setattr(obj, "fetch", self.apply_middleware(obj.fetch, obj))

    @staticmethod
    def apply_middleware(func: FT, instance: Union[Driver, AsyncDriver]) -> FT:
        if asyncio.iscoroutinefunction(func):

            async def wrapper(*args, **kwargs):
                handler = func
                for middleware in instance.middleware:
                    handler = middleware(handler)
                return await handler(*args, **kwargs)

        else:

            def wrapper(*args, **kwargs):
                handler = func
                for middleware in instance.middleware:
                    handler = middleware(handler)
                return handler(*args, **kwargs)

        return cast(FT, functools.wraps(func)(wrapper))
