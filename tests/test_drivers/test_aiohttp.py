# pylint: disable=import-outside-toplevel,redefined-outer-name

import uuid
from http.cookies import SimpleCookie
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


async def test_cookies(aresponses, driver: "AioHttpDriver"):
    def echo_cookies(request):
        return aresponses.Response(
            status=200, headers={"Set-Cookie": request.headers["Cookie"]}
        )

    aresponses.add("example.com", "/", "GET", echo_cookies)

    cookies = {"csrftoken": "YWxhZGRpbjpvcGVuc2VzYW1l"}
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = await wrapper.echo_cookies(cookies)
    assert isinstance(response.cookies, SimpleCookie)
    assert response.cookies["csrftoken"].value == cookies["csrftoken"]


@pytest.mark.parametrize("method", ["send_data_as_dict", "send_data_as_tuples"])
async def test_send_data(aresponses, driver: "AioHttpDriver", method: str):
    async def echo_data(request):
        return aresponses.Response(status=200, body=await request.text())

    aresponses.add("example.com", "/", "POST", echo_data)

    form_data = "name=apiwrappers&tags=api&tags=wrapper&pre-release=True&version=1"
    wrapper = APIWrapper("https://example.com", driver=driver)

    response = await getattr(wrapper, method)()
    assert await response.text() == form_data
