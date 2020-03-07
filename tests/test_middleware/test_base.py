# pylint: disable=unused-argument

from typing import Awaitable, cast

import pytest

from apiwrappers import Method, Request, Response
from apiwrappers.middleware import BaseMiddleware

from .. import factories


def test_base_middleware() -> None:
    def handler(request: Request, *args, **kwargs) -> Response:
        return factories.make_response(b"Hello, World!")

    request = Request(Method.GET, "https://example.com")
    response = BaseMiddleware(handler)(request)
    assert response.content == b"Hello, World!"


@pytest.mark.asyncio
async def test_base_middleware_async() -> None:
    async def handler(request: Request, *args, **kwargs) -> Response:
        return factories.make_response(b"Hello, World!")

    request = Request(Method.GET, "https://example.com")
    # see https://github.com/python/mypy/issues/8283
    response = await cast(Awaitable[Response], BaseMiddleware(handler)(request))
    assert response.content == b"Hello, World!"


def test_base_middleware_handler_raises_exception() -> None:
    def handler(request: Request, *args, **kwargs) -> Response:
        raise Exception("You shall not pass")

    request = Request(Method.GET, "https://example.com")
    with pytest.raises(Exception):
        BaseMiddleware(handler)(request)


@pytest.mark.asyncio
async def test_base_middleware_handler_raises_exception_async() -> None:
    async def handler(request: Request, *args, **kwargs) -> Response:
        raise Exception("You shall not pass")

    request = Request(Method.GET, "https://example.com")
    with pytest.raises(Exception):
        # see https://github.com/python/mypy/issues/8283
        await cast(Awaitable[Response], BaseMiddleware(handler)(request))
