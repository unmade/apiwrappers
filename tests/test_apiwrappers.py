from dataclasses import dataclass
from typing import Generic, TypeVar

import pytest

from apiwrappers import AsyncDriver, Driver, Fetch, Method, Request

from . import factories

DT = TypeVar("DT", Driver, AsyncDriver)


@dataclass
class User:
    user_id: int


class APIWrapper(Generic[DT]):
    user = Fetch(User)

    def __init__(self, driver: DT):
        self.driver: DT = driver

    @user.request
    def user_request(self, user_id: int) -> Request:
        # pylint: disable=no-self-use
        return Request(Method.GET, "https://example.com", f"/users/{user_id}")


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


def test_fetch_as_descriptor() -> None:
    response = factories.make_response(b'{"user_id": 1}')
    driver = factories.make_driver(response)
    wrapper = APIWrapper(driver=driver)
    user = wrapper.user(user_id=1)
    assert isinstance(user, User)


@pytest.mark.asyncio
async def test_fetch_as_descriptor_with_async_driver() -> None:
    response = factories.make_response(b'{"user_id": 1}')
    driver = factories.make_async_driver(response)
    wrapper = APIWrapper(driver=driver)
    user = await wrapper.user(user_id=1)
    assert isinstance(user, User)
