import pytest

from apiwrappers import Method, Request

from . import factories


def test_driver_protocol() -> None:
    response = factories.make_response(b'"Hello, World!"')
    driver = factories.make_driver(response)
    request = Request(Method.GET, "https://example.com", "/")
    response = driver.fetch(request)
    assert response.status_code == 200
    assert response.text() == '"Hello, World!"'
    assert response.json() == "Hello, World!"


@pytest.mark.asyncio
async def test_async_driver_protocol() -> None:
    response = factories.make_response(b'"Hello, World!"')
    driver = factories.make_async_driver(response)
    request = Request(Method.GET, "https://example.com", "/")
    response = await driver.fetch(request)
    assert response.status_code == 200
    assert response.text() == '"Hello, World!"'
    assert response.json() == "Hello, World!"
