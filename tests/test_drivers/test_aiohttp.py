# pylint: disable=import-outside-toplevel,redefined-outer-name

import uuid
from typing import TYPE_CHECKING

import pytest

from apiwrappers.entities import QueryParams
from apiwrappers.structures import CaseInsensitiveDict

from .wrappers import APIWrapper

if TYPE_CHECKING:
    from apiwrappers.drivers.aiohttp import AioHttpDriver


pytestmark = [pytest.mark.aiohttp, pytest.mark.asyncio]


@pytest.fixture
async def driver():
    from apiwrappers.drivers.aiohttp import AioHttpDriver

    return AioHttpDriver()


async def test_get_text(aresponses, driver: "AioHttpDriver"):
    aresponses.add(
        "example.com", "/", "GET", "Hello, World!",
    )
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = await wrapper.get_hello_world()
    assert response.status_code == 200
    assert await response.text() == "Hello, World!"


async def test_get_json(aresponses, driver: "AioHttpDriver"):
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


async def test_headers(aresponses, driver: "AioHttpDriver"):
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


async def test_query_params(aresponses, driver: "AioHttpDriver"):
    def echo_url_path(request):
        return aresponses.Response(
            status=200, body=f"{request.url.path}?{request.url.query_string}",
        )

    query_params: QueryParams = {"type": "user", "id": ["1", "2"], "name": None}
    path = "/?type=user&id=1&id=2"
    aresponses.add("example.com", path, "GET", echo_url_path, match_querystring=True)

    wrapper = APIWrapper("https://example.com", driver=driver)
    response = await wrapper.echo_query_params(query_params)
    assert await response.text() == path
