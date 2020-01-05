# pylint: disable=import-outside-toplevel,redefined-outer-name

import pytest

from apiwrappers import Method, Request

pytestmark = [pytest.mark.aiohttp, pytest.mark.asyncio]


@pytest.fixture
async def driver():
    from apiwrappers.drivers.aiohttp import AioHttpDriver

    return AioHttpDriver()


async def test_driver_fetch_content(aresponses, driver):
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
