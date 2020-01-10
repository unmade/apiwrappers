# pylint: disable=no-self-use,unused-argument

from http.cookies import SimpleCookie
from typing import Union

import pytest

from apiwrappers import AsyncDriver, Driver, Method, Request, Response
from apiwrappers.structures import CaseInsensitiveDict

RESPONSE = Response(
    status_code=200,
    url="https://example.com/foos",
    headers=CaseInsensitiveDict(),
    cookies=SimpleCookie(),
    encoding="utf-8",
    content=b'"Hello, World!"',
)


class DriverMock:
    def fetch(self, request: Request):
        return RESPONSE


class AsyncDriverMock:
    async def fetch(self, request: Request):
        return RESPONSE


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
    assert response.text() == '"Hello, World!"'
    assert response.json() == "Hello, World!"


@pytest.mark.asyncio
async def test_async_driver_protocol():
    driver = AsyncDriverMock()
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = await wrapper.list_foo()
    assert response.status_code == 200
    assert response.text() == '"Hello, World!"'
    assert response.json() == "Hello, World!"
