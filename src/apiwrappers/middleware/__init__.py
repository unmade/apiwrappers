import asyncio
import functools
from typing import Any, Callable, TypeVar, cast

from apiwrappers.middleware.auth import Authorization
from apiwrappers.middleware.base import BaseMiddleware  # noqa: F401

FuncType = Callable[..., Any]
FT = TypeVar("FT", bound=FuncType)


def apply_middleware(func: FT) -> FT:
    if asyncio.iscoroutinefunction(func):

        async def wrapper(instance, *args, **kwargs):
            handler = functools.partial(func, instance)
            for wrap in [Authorization] + instance.middleware:
                handler = wrap(handler)
            return await handler(*args, **kwargs)

    else:

        def wrapper(instance, *args, **kwargs):
            handler = functools.partial(func, instance)
            for wrap in [Authorization] + instance.middleware:
                handler = wrap(handler)
            return handler(*args, **kwargs)

    return cast(FT, functools.wraps(func)(wrapper))
