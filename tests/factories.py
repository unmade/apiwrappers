import dataclasses
from http.cookies import SimpleCookie
from typing import Any, Dict, Type, Union

from apiwrappers import AsyncDriver, Driver, Method, Request, Response
from apiwrappers.middleware import MiddlewareChain
from apiwrappers.protocols import AsyncMiddleware, Middleware
from apiwrappers.structures import CaseInsensitiveDict, NoValue
from apiwrappers.typedefs import ClientCert, Timeout, Verify


class DriverMock:
    middleware = MiddlewareChain()
    timeout: Timeout = 1
    verify: Verify = True
    cert: ClientCert = None

    def __init__(self, response: Response):
        self.response = response

    @middleware.wrap
    def fetch(
        self,
        request: Request,
        timeout: Union[Timeout, NoValue] = NoValue(),
    ) -> Response:
        # pylint: disable=unused-argument
        return dataclasses.replace(self.response, request=request)


class AsyncDriverMock:
    middleware = MiddlewareChain()
    timeout: Timeout = 1
    verify: Verify = True
    cert: ClientCert = None

    def __init__(self, response: Response):
        self.response = response

    @middleware.wrap
    async def fetch(
        self,
        request: Request,
        timeout: Union[Timeout, NoValue] = NoValue(),
    ) -> Response:
        # pylint: disable=unused-argument
        return dataclasses.replace(self.response, request=request)


def make_response(content: bytes, **kwargs) -> Response:
    defaults: Dict[str, Any] = {
        "request": Request(Method.GET, "https://example.com"),
        "status_code": 200,
        "url": "https://example.com/",
        "headers": CaseInsensitiveDict(),
        "cookies": SimpleCookie(),
        "encoding": "utf-8",
        "content": content,
    }
    defaults.update(kwargs)
    return Response(**defaults)


def make_driver(response: Response, *middleware: Type[Middleware]) -> Driver:
    driver = DriverMock(response)
    driver.middleware = middleware
    return driver


def make_async_driver(
    response: Response, *middleware: Type[AsyncMiddleware]
) -> AsyncDriver:
    driver = AsyncDriverMock(response)
    driver.middleware = middleware
    return driver
