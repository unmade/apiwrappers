# pylint: disable=import-outside-toplevel,redefined-outer-name

import uuid

import pytest

from apiwrappers.structures import CaseInsensitiveDict

from .wrappers import APIWrapper

pytestmark = [pytest.mark.aiohttp, pytest.mark.asyncio]


@pytest.fixture
async def driver():
    from apiwrappers.drivers.aiohttp import AioHttpDriver

    return AioHttpDriver()


async def test_get_text(aresponses, driver):
    aresponses.add(
        "example.com", "/", "GET", "Hello, World!",
    )
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = await wrapper.get_hello_world()
    assert response.status_code == 200
    assert await response.text() == "Hello, World!"


async def test_get_json(aresponses, driver):
    aresponses.add(
        "example.com",
        "/",
        "GET",
        aresponses.Response(
            body=b'{"message": "Hello, World!"}', content_type="application/json"
        ),
    )
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = await wrapper.get_hello_world()
    assert response.status_code == 200
    assert await response.json() == {"message": "Hello, World!"}


async def test_headers(aresponses, driver):
    def echo_headers(request):
        return aresponses.Response(
            status=200,
            headers={"X-Response-ID": request.headers["X-Request-ID"]},
            body=b'{"code": 200, "message": "ok"}',
        )

    aresponses.add("example.com", "/", "POST", echo_headers)

    headers = {"X-Request-ID": str(uuid.uuid4())}
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = await wrapper.echo_headers(headers)
    assert isinstance(response.headers, CaseInsensitiveDict)
    assert response.headers["X-Response-ID"] == headers["X-Request-ID"]
