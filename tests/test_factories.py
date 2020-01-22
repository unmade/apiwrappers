# pylint: disable=import-outside-toplevel

from dataclasses import dataclass

import pytest

from apiwrappers import Method, Request, make_driver, make_response

from . import factories


@dataclass
class User:
    id: int


def test_make_driver_unexisting_driver() -> None:
    with pytest.raises(ValueError):
        make_driver("driver_does_not_exists")


@pytest.mark.requests
def test_make_driver_requests() -> None:
    from apiwrappers.drivers.requests import RequestsDriver

    driver = make_driver("requests")
    assert isinstance(driver, RequestsDriver)


@pytest.mark.aiohttp
def test_make_driver_aiohttp() -> None:
    from apiwrappers.drivers.aiohttp import AioHttpDriver

    driver = make_driver("aiohttp")
    assert isinstance(driver, AioHttpDriver)


def test_response_returns_response() -> None:
    request = Request(Method.GET, "https://example.com", "/")
    driver_response = factories.make_response(b"Hello, World")
    driver = factories.make_driver(driver_response)
    response = make_response(driver, request)
    assert response.content == b"Hello, World"


@pytest.mark.asyncio
async def test_response_returns_response_async() -> None:
    request = Request(Method.GET, "https://example.com", "/")
    driver_response = factories.make_response(b"Hello, World")
    driver = factories.make_async_driver(driver_response)
    response = await make_response(driver, request)
    assert response.content == b"Hello, World"


def test_response_returns_model() -> None:
    request = Request(Method.GET, "https://example.com", "/")
    driver_response = factories.make_response(b'{"id": 1}')
    driver = factories.make_driver(driver_response)
    user = make_response(driver, request, model=User)
    assert user == User(id=1)


@pytest.mark.asyncio
async def test_response_returns_model_async() -> None:
    request = Request(Method.GET, "https://example.com", "/")
    driver_response = factories.make_response(b'{"id": 1}')
    driver = factories.make_async_driver(driver_response)
    user = await make_response(driver, request, model=User)
    assert user == User(id=1)


def test_response_returns_model_from_source() -> None:
    request = Request(Method.GET, "https://example.com", "/")
    driver_response = factories.make_response(b'{"user": {"id": 1}}')
    driver = factories.make_driver(driver_response)
    user = make_response(driver, request, model=User, source="user")
    assert user == User(id=1)


@pytest.mark.asyncio
async def test_response_returns_model_from_source_async() -> None:
    request = Request(Method.GET, "https://example.com", "/")
    driver_response = factories.make_response(b'{"user": {"id": 1}}')
    driver = factories.make_async_driver(driver_response)
    user = await make_response(driver, request, model=User, source="user")
    assert user == User(id=1)
