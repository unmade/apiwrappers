from http.cookies import SimpleCookie
from typing import Any, Dict, Union

from apiwrappers import AsyncDriver, Driver, Request, Response
from apiwrappers.structures import CaseInsensitiveDict
from apiwrappers.typedefs import Timeout
from apiwrappers.utils import NoValue


def make_response(content: bytes, **kwargs) -> Response:
    defaults: Dict[str, Any] = {
        "status_code": 200,
        "url": "https://example.com/",
        "headers": CaseInsensitiveDict(),
        "cookies": SimpleCookie(),
        "encoding": "utf-8",
        "content": content,
    }
    defaults.update(kwargs)
    return Response(**defaults)


def make_driver(response: Response) -> Driver:
    class DriverMock:
        # pylint: disable=unused-argument,no-self-use
        timeout: Timeout = 1
        verify_ssl: bool = True

        def fetch(
            self,
            request: Request,
            timeout: Union[Timeout, NoValue] = NoValue(),
            verify_ssl: Union[bool, NoValue] = NoValue(),
        ) -> Response:
            return response

    return DriverMock()


def make_async_driver(response: Response) -> AsyncDriver:
    class AsyncDriverMock:
        # pylint: disable=unused-argument,no-self-use
        timeout: Timeout = 1
        verify_ssl: bool = True

        async def fetch(
            self,
            request: Request,
            timeout: Union[Timeout, NoValue] = NoValue(),
            verify_ssl: Union[bool, NoValue] = NoValue(),
        ) -> Response:
            return response

    return AsyncDriverMock()
