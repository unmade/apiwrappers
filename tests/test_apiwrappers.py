from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, Mapping, TypeVar

import pytest

from apiwrappers import AsyncDriver, Driver, Fetch, Method, Request

from . import factories

UT = TypeVar("UT", bound="User")
DT = TypeVar("DT", Driver, AsyncDriver)


@dataclass
class User:
    user_id: int

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> User:
        return cls(user_id=int(data["user_id"]))


class APIWrapper(Generic[DT]):
    user = Fetch(User.from_dict)

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
    user = Fetch(User.from_dict).response(driver, request)
    assert isinstance(user, User)
    assert user.user_id == 1


@pytest.mark.asyncio
async def test_fetch_response_with_async_driver() -> None:
    response = factories.make_response(b'{"user_id": 1}')
    driver = factories.make_async_driver(response)
    request = Request(Method.GET, "https://example.com", "/users/1")
    user = await Fetch(User.from_dict).response(driver, request)
    assert isinstance(user, User)
    assert user.user_id == 1


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


def test_fetch_source() -> None:
    response = factories.make_response(b'{"data": {"user_id": 1}}')
    driver = factories.make_driver(response)
    request = Request(Method.GET, "https://example.com", "/users/1")
    user = Fetch(User.from_dict, source="data").response(driver, request)
    assert isinstance(user, User)
    assert user.user_id == 1


@pytest.mark.asyncio
async def test_fetch_source_with_async_driver() -> None:
    response = factories.make_response(b'{"data": {"user_id": 1}}')
    driver = factories.make_async_driver(response)
    request = Request(Method.GET, "https://example.com", "/users/1")
    user = await Fetch(User.from_dict, source="data").response(driver, request)
    assert isinstance(user, User)
    assert user.user_id == 1
