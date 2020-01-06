# pylint: disable=import-outside-toplevel,redefined-outer-name

import uuid

import pytest

from apiwrappers import Method, Request
from apiwrappers.structures import CaseInsensitiveDict

pytestmark = [pytest.mark.aiohttp, pytest.mark.asyncio]


@pytest.fixture
async def driver():
    from apiwrappers.drivers.aiohttp import AioHttpDriver

    return AioHttpDriver()


async def test_fetch(aresponses, driver):
    body = '{"code": 200, "message": "ok"}'
    aresponses.add(
        "example.com",
        "/users",
        "POST",
        aresponses.Response(body=body, content_type="application/json"),
    )
    request = Request(
        Method.POST, "https://example.com", "/users", json={"foo": "bar"},
    )
    response = await driver.fetch(request)
    assert response.status_code == 200
    assert await response.json() == {"code": 200, "message": "ok"}
    assert await response.text() == body


async def test_headers(aresponses, driver):
    def set_header(request):
        return aresponses.Response(
            status=200,
            headers={"X-Response-ID": request.headers["X-Request-ID"]},
            body=b'{"code": 200, "message": "ok"}',
        )

    aresponses.add("example.com", "/", "POST", set_header)

    request = Request(
        Method.POST,
        "https://example.com",
        "/",
        headers={"X-Request-ID": str(uuid.uuid4())},
    )
    response = await driver.fetch(request)
    assert isinstance(response.headers, CaseInsensitiveDict)
    assert response.headers["X-Response-ID"] == request.headers["X-Request-ID"]
