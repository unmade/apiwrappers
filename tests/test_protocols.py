# pylint: disable=no-self-use,unused-argument

import asyncio
from typing import Union

from apiwrappers import AsyncDriver, AsyncResponse, Driver, Method, Request, Response


class DriverMock:
    def fetch(self, request: Request):
        def text():
            return "Hello, World!"

        def json():
            return "Hello, World!"

        return Response(
            status_code=200,
            url="https://example.com/foos",
            headers={},
            cookies={},
            encoding="utf-8",
            content=b"Hello, World!",
            text=text,
            json=json,
        )


class AsyncDriverMock:
    async def fetch(self, request: Request):
        async def text():
            return "Hello, World!"

        async def json():
            return "Hello, World!"

        return AsyncResponse(
            status_code=200,
            url="https://example.com/foos",
            headers={},
            cookies={},
            encoding="utf-8",
            content=b"Hello, World!",
            text=text,
            json=json,
        )


class APIWrapper:
    def __init__(self, host: str, driver: Union[Driver, AsyncDriver]):
        self.host = host
        self.driver = driver

    def list_foo(self):
        request = Request(Method.GET, self.host, "/foos")
        return self.driver.fetch(request)


def test_driver_protocol():
    driver = DriverMock()
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = wrapper.list_foo()
    assert response.status_code == 200
    assert response.text() == "Hello, World!"
    assert response.json() == "Hello, World!"


def test_async_driver_protocol():
    driver = AsyncDriverMock()
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = asyncio.run(wrapper.list_foo())
    assert response.status_code == 200
    assert asyncio.run(response.text()) == "Hello, World!"
    assert asyncio.run(response.json()) == "Hello, World!"
