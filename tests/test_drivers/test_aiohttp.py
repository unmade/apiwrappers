# pylint: disable=import-outside-toplevel,too-many-lines

from __future__ import annotations

import asyncio
import json
import uuid
from http.cookies import SimpleCookie
from typing import TYPE_CHECKING, Type
from unittest import mock

import pytest

from apiwrappers import exceptions
from apiwrappers.entities import QueryParams
from apiwrappers.protocols import AsyncMiddleware
from apiwrappers.structures import CaseInsensitiveDict, NoValue

from .middleware import RequestMiddleware, ResponseMiddleware
from .wrappers import APIWrapper

if TYPE_CHECKING:
    from aiohttp.web import Request
    from apiwrappers.drivers.aiohttp import AioHttpDriver


pytestmark = [pytest.mark.aiohttp, pytest.mark.asyncio]


def aiohttp_driver(*middleware: Type[AsyncMiddleware], **kwargs) -> AioHttpDriver:
    from apiwrappers.drivers.aiohttp import AioHttpDriver

    return AioHttpDriver(*middleware, **kwargs)


async def echo(request: Request):
    from aiohttp.web import Response

    # Zero Content-Length causing parsing error so remove it
    # https://github.com/aio-libs/aiohttp/issues/3641
    excluded = ("content-length",)
    headers = {k: v for k, v in request.headers.items() if k.lower() not in excluded}

    if "Cookie" in request.headers:
        headers["Set-Cookie"] = request.headers["Cookie"]

    try:
        body = json.loads(await request.text())  # type: ignore
    except (TypeError, ValueError):
        body = await request.text()

    return Response(
        status=200,
        headers=headers,
        body=json.dumps(
            {
                "path_url": f"{request.url.path}?{request.url.query_string}",
                "body": body,
            }
        ),
    )


async def test_representation() -> None:
    driver = aiohttp_driver()
    setattr(driver, "_middleware", [])
    assert repr(driver) == "AioHttpDriver(timeout=300, verify_ssl=True)"


async def test_representation_with_middleware() -> None:
    driver = aiohttp_driver(RequestMiddleware, ResponseMiddleware)
    assert repr(driver) == (
        "AioHttpDriver("
        "Authentication, RequestMiddleware, ResponseMiddleware, "
        "timeout=300, verify_ssl=True"
        ")"
    )


async def test_string_representation() -> None:
    driver = aiohttp_driver()
    assert str(driver) == "<AsyncDriver 'aiohttp'>"


async def test_get_content(aresponses) -> None:
    aresponses.add("example.com", "/", "GET", "Hello, World!")
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.get_hello_world()
    assert response.status_code == 200
    assert response.content == b"Hello, World!"


async def test_get_text(aresponses) -> None:
    aresponses.add("example.com", "/", "GET", "Hello, World!")
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.get_hello_world()
    assert response.status_code == 200
    assert response.text() == "Hello, World!"


async def test_get_json(aresponses) -> None:
    aresponses.add(
        "example.com",
        "/",
        "GET",
        aresponses.Response(
            body=b'{"message": "Hello, World!"}', content_type="application/json"
        ),
    )
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.get_hello_world()
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


async def test_headers(aresponses) -> None:
    aresponses.add("example.com", "/", "POST", echo)
    headers = {"X-Request-ID": str(uuid.uuid4())}
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.echo_headers(headers)
    assert isinstance(response.headers, CaseInsensitiveDict)
    assert response.headers["X-Request-ID"] == headers["X-Request-ID"]


async def test_query_params(aresponses) -> None:
    query_params: QueryParams = {"type": "user", "id": ["1", "2"], "name": None}
    path = "/?type=user&id=1&id=2"
    aresponses.add("example.com", path, "GET", echo, match_querystring=True)
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.echo_query_params(query_params)
    assert response.json()["path_url"] == path  # type: ignore


async def test_cookies(aresponses) -> None:
    aresponses.add("example.com", "/", "GET", echo)
    cookies = {"csrftoken": "YWxhZGRpbjpvcGVuc2VzYW1l"}
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.echo_cookies(cookies)
    assert isinstance(response.cookies, SimpleCookie)
    assert response.cookies["csrftoken"].value == cookies["csrftoken"]


@pytest.mark.parametrize(
    "payload",
    [
        {
            "name": "apiwrappers",
            "tags": ["api", "wrapper"],
            "pre-release": True,
            "version": 1,
        },
        [
            ("name", "apiwrappers"),
            ("tags", "api"),
            ("tags", "wrapper"),
            ("pre-release", True),
            ("version", 1),
        ],
    ],
)
async def test_send_data(aresponses, payload) -> None:
    aresponses.add("example.com", "/", "POST", echo)
    form_data = "name=apiwrappers&tags=api&tags=wrapper&pre-release=True&version=1"
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.send_data(payload)
    assert response.json()["body"] == form_data  # type: ignore


async def test_send_json(aresponses) -> None:
    aresponses.add("example.com", "/", "POST", echo)

    payload = {
        "name": "apiwrappers",
        "tags": ["api", "wrapper"],
        "pre-release": True,
        "version": 1,
    }

    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.send_json(payload)
    assert response.json()["body"] == payload  # type: ignore


@pytest.mark.parametrize(
    ["driver_timeout", "fetch_timeout", "expected"],
    [
        (None, None, None),
        (None, 0.5, 0.5),
        (300, None, None),
        (300, 1, 1),
        (300, NoValue(), 300),
    ],
)
async def test_timeout(aresponses, driver_timeout, fetch_timeout, expected) -> None:
    # pylint: disable=protected-access
    # aiohttp calls are hard to mock, instead just fire a call and test private method
    aresponses.add("example.com", "/", "GET")
    driver = aiohttp_driver(timeout=driver_timeout)
    wrapper = APIWrapper("https://example.com", driver=driver)
    await wrapper.timeout(fetch_timeout)
    assert driver._prepare_timeout(fetch_timeout) == expected


async def test_no_timeout(aresponses) -> None:
    # pylint: disable=protected-access
    # aiohttp calls are hard to mock, instead just fire a call and test private method
    aresponses.add("example.com", "/", "GET")
    driver = aiohttp_driver(timeout=None)
    wrapper = APIWrapper("https://example.com", driver=driver)
    await wrapper.timeout(None)
    assert driver._prepare_timeout(None) is None


@pytest.mark.parametrize(
    ["driver_ssl", "fetch_ssl", "expected"],
    [
        (True, True, True),
        (True, False, False),
        (False, False, False),
        (False, True, True),
        (False, NoValue(), False),
        (True, NoValue(), True),
    ],
)
async def test_verify_ssl(aresponses, driver_ssl, fetch_ssl, expected) -> None:
    # pylint: disable=protected-access
    # aiohttp calls are hard to mock, instead just fire a call and test private method
    aresponses.add("example.com", "/", "GET")
    driver = aiohttp_driver(verify_ssl=driver_ssl)
    wrapper = APIWrapper("https://example.com", driver=driver)
    await wrapper.verify_ssl(fetch_ssl)
    assert driver._prepare_ssl(fetch_ssl) == expected


async def test_reraise_client_error() -> None:
    import aiohttp

    async def client_error(*args, **kwargs):
        raise aiohttp.ClientError

    with mock.patch.object(aiohttp.ClientSession, "request", client_error):
        wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
        with pytest.raises(exceptions.DriverError) as exc:
            await wrapper.exception()
        assert not isinstance(exc.value, exceptions.ConnectionFailed)


async def test_reraise_client_connection_error(aresponses) -> None:
    import aiohttp

    aresponses.add("example.com", "/", "GET", response=aiohttp.ClientConnectionError())
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    with pytest.raises(exceptions.ConnectionFailed):
        await wrapper.exception()


async def test_reraise_timeout_error() -> None:
    import aiohttp

    async def timeout_error(*args, **kwargs):
        raise asyncio.TimeoutError

    with mock.patch.object(aiohttp.ClientSession, "request", timeout_error):
        wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
        with pytest.raises(exceptions.Timeout):
            await wrapper.exception()


@pytest.mark.parametrize(
    "response",
    [
        {"body": b"Plaint Text"},
        {"body": b"Plaint Text", "content_type": "application/json"},
    ],
)
async def test_invalid_json_response(aresponses, response) -> None:
    aresponses.add("example.com", "/", "GET", aresponses.Response(**response))
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    json_response = await wrapper.get_hello_world()
    with pytest.raises(json.JSONDecodeError):
        json_response.json()


async def test_middleware(aresponses) -> None:
    aresponses.add("example.com", "/", "GET", echo)
    driver = aiohttp_driver(RequestMiddleware, ResponseMiddleware)
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = await wrapper.middleware()
    assert response.headers["x-request-id"] == "request_middleware"
    assert response.headers["x-response-id"] == "response_middleware"


async def test_basic_auth(aresponses) -> None:
    aresponses.add("example.com", "/", "GET", echo)
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.basic_auth()
    assert "Basic " in response.headers["Authorization"]


async def test_token_auth(aresponses) -> None:
    aresponses.add("example.com", "/", "GET", echo)
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.token_auth()
    assert "Bearer " in response.headers["Authorization"]


async def test_complex_auth_flow(aresponses) -> None:
    aresponses.add(
        "example.com",
        "/auth",
        "POST",
        aresponses.Response(
            body=b'{"token": "authtoken"}', content_type="application/json"
        ),
    )
    aresponses.add("example.com", "/", "GET", echo)
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.complex_auth_flow()
    assert response.headers["Authorization"] == "Bearer authtoken"
