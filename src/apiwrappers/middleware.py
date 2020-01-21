import asyncio
import functools
from typing import (
    Any,
    Awaitable,
    Callable,
    Generic,
    NoReturn,
    TypeVar,
    Union,
    cast,
    overload,
)

from apiwrappers.entities import Request, Response
from apiwrappers.protocols import AsyncHandler, Handler
from apiwrappers.structures import NoValue
from apiwrappers.typedefs import Timeout

FuncType = Callable[..., Any]
FT = TypeVar("FT", bound=FuncType)
T = TypeVar("T", Handler, AsyncHandler)


def iscoroutinehandler(handler: Union[Handler, AsyncHandler]) -> bool:
    return (
        asyncio.iscoroutinefunction(getattr(handler, "handler", None))  # middleware
        or asyncio.iscoroutinefunction(getattr(handler, "func", None))  # partial
        or asyncio.iscoroutinefunction(
            getattr(getattr(handler, "handler", None), "func", None)
        )
        or asyncio.iscoroutinefunction(handler)
    )


def apply_middleware(func: FT) -> FT:
    if asyncio.iscoroutinefunction(func):

        async def wrapper(instance, *args, **kwargs):
            handler = functools.partial(func, instance)
            for wrap in instance.middleware:
                handler = wrap(handler)
            return await handler(*args, **kwargs)

    else:

        def wrapper(instance, *args, **kwargs):
            handler = functools.partial(func, instance)
            for wrap in instance.middleware:
                handler = wrap(handler)
            return handler(*args, **kwargs)

    return cast(FT, functools.wraps(func)(wrapper))


class BaseMiddleware(Generic[T]):
    # pylint: disable=no-self-use,unused-argument

    def __init__(self, handler: T):
        self.handler: T = handler

    # NOTE: overloading __call__ with self-type doesn't work correctly
    # see https://github.com/python/mypy/issues/8283
    @overload
    def __call__(
        self: "BaseMiddleware[Handler]",
        request: Request,
        timeout: Union[Timeout, NoValue] = NoValue(),
        verify_ssl: Union[bool, NoValue] = NoValue(),
    ) -> Response:
        ...

    @overload
    def __call__(
        self: "BaseMiddleware[AsyncHandler]",
        request: Request,
        timeout: Union[Timeout, NoValue] = NoValue(),
        verify_ssl: Union[bool, NoValue] = NoValue(),
    ) -> Awaitable[Response]:
        ...

    def __call__(self, request, timeout=NoValue(), verify_ssl=NoValue()):
        if iscoroutinehandler(self.handler):
            call_next = self.call_next_async
        else:
            call_next = self.call_next
        return call_next(self.handler, request, timeout=timeout, verify_ssl=verify_ssl)

    def process_request(self, request: Request) -> Request:
        return request

    def process_response(self, response: Response) -> Response:
        return response

    def process_exception(self, request: Request, exception: Exception) -> NoReturn:
        raise exception

    def call_next(
        self, handler: Handler, request: Request, *args, **kwargs,
    ) -> Response:
        request = self.process_request(request)
        try:
            response = handler(request, *args, **kwargs)
        except Exception as exc:  # pylint: disable=broad-except
            self.process_exception(request, exc)
        else:
            return self.process_response(response)

    async def call_next_async(
        self, handler: AsyncHandler, request: Request, *args, **kwargs,
    ) -> Response:
        request = self.process_request(request)
        try:
            response = await handler(request, *args, **kwargs)
        except Exception as exc:  # pylint: disable=broad-except
            self.process_exception(request, exc)
        else:
            return self.process_response(response)
