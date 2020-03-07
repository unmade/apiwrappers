from dataclasses import dataclass

import pytest

from apiwrappers import Method, Request, fetch

from . import factories


@dataclass
class User:
    id: int


def test_fetch_returns_response() -> None:
    request = Request(Method.GET, "https://example.com")
    driver_response = factories.make_response(b"Hello, World")
    driver = factories.make_driver(driver_response)
    response = fetch(driver, request)
    assert response.content == b"Hello, World"


@pytest.mark.asyncio
async def test_fetch_returns_response_async() -> None:
    request = Request(Method.GET, "https://example.com")
    driver_response = factories.make_response(b"Hello, World")
    driver = factories.make_async_driver(driver_response)
    response = await fetch(driver, request)
    assert response.content == b"Hello, World"


def test_fetch_returns_model() -> None:
    request = Request(Method.GET, "https://example.com")
    driver_response = factories.make_response(b'{"id": 1}')
    driver = factories.make_driver(driver_response)
    user = fetch(driver, request, model=User)
    assert user == User(id=1)


@pytest.mark.asyncio
async def test_fetch_returns_model_async() -> None:
    request = Request(Method.GET, "https://example.com")
    driver_response = factories.make_response(b'{"id": 1}')
    driver = factories.make_async_driver(driver_response)
    user = await fetch(driver, request, model=User)
    assert user == User(id=1)


def test_fetch_returns_model_from_source() -> None:
    request = Request(Method.GET, "https://example.com")
    driver_response = factories.make_response(b'{"user": {"id": 1}}')
    driver = factories.make_driver(driver_response)
    user = fetch(driver, request, model=User, source="user")
    assert user == User(id=1)


@pytest.mark.asyncio
async def test_fetch_returns_model_from_source_async() -> None:
    request = Request(Method.GET, "https://example.com")
    driver_response = factories.make_response(b'{"user": {"id": 1}}')
    driver = factories.make_async_driver(driver_response)
    user = await fetch(driver, request, model=User, source="user")
    assert user == User(id=1)
