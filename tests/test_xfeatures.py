from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

import pytest

from apiwrappers import AsyncDriver, Driver, Method, Request, Url
from apiwrappers.xfeatures import Fetch

from . import factories

DT = TypeVar("DT", Driver, AsyncDriver)


@dataclass
class User:
    user_id: int


class APIWrapper(Generic[DT]):
    user = Fetch(User)

    def __init__(self, driver: DT):
        self.url = Url("https://example.com")
        self.driver: DT = driver

    @user.request
    def user_request(self, user_id: int) -> Request:
        return Request(Method.GET, self.url("/users/{user_id}", user_id=user_id))


def test_fetch_as_descriptor() -> None:
    response = factories.make_response(b'{"user_id": 1}')
    driver = factories.make_driver(response)
    wrapper = APIWrapper(driver=driver)
    user = wrapper.user(user_id=1)
    assert isinstance(user, User)
    assert user.user_id == 1


@pytest.mark.asyncio
async def test_fetch_as_descriptor_with_async_driver() -> None:
    response = factories.make_response(b'{"user_id": 1}')
    driver = factories.make_async_driver(response)
    wrapper = APIWrapper(driver=driver)
    user = await wrapper.user(user_id=1)
    assert isinstance(user, User)
    assert user.user_id == 1
