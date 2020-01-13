from dataclasses import dataclass

import pytest

from apiwrappers import Fetch, Method, Request

from . import factories


@dataclass
class User:
    user_id: int


def test_fetch_response() -> None:
    response = factories.make_response(b'{"user_id": 1}')
    driver = factories.make_driver(response)
    request = Request(Method.GET, "https://example.com", "/users/1")
    user = Fetch(User).response(driver, request)
    assert isinstance(user, User)


@pytest.mark.asyncio
async def test_fetch_response_with_async_driver() -> None:
    response = factories.make_response(b'{"user_id": 1}')
    driver = factories.make_async_driver(response)
    request = Request(Method.GET, "https://example.com", "/users/1")
    user = await Fetch(User).response(driver, request)
    assert isinstance(user, User)
