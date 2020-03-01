# pylint: disable=import-outside-toplevel,redefined-outer-name

from __future__ import annotations

import json
import re
import uuid
from http.cookies import SimpleCookie
from typing import TYPE_CHECKING, Type

import pytest

from apiwrappers import exceptions
from apiwrappers.entities import QueryParams
from apiwrappers.protocols import AsyncMiddleware
from apiwrappers.structures import CaseInsensitiveDict, NoValue

from .middleware import RequestMiddleware, ResponseMiddleware
from .wrappers import APIWrapper

if TYPE_CHECKING:
    from aioresponses import aioresponses
    from apiwrappers.drivers.aiohttp import AioHttpDriver


pytestmark = [pytest.mark.aiohttp, pytest.mark.asyncio]


@pytest.fixture
def responses():
    from aioresponses import aioresponses

    with aioresponses() as mocked_responses:
        yield mocked_responses


def aiohttp_driver(*middleware: Type[AsyncMiddleware], **kwargs) -> AioHttpDriver:
    from apiwrappers.drivers.aiohttp import AioHttpDriver

    return AioHttpDriver(*middleware, **kwargs)


async def echo(url, **kwargs):
    from aioresponses import CallbackResult
    from aiohttp import ClientResponse, hdrs

    # see: https://github.com/pnuckowski/aioresponses/issues/155
    class Response(ClientResponse):
        def headers_getter(self):
            return self.__headers

        def headers_setter(self, value):
            self.__headers = value
            for hdr in value.getall(hdrs.SET_COOKIE, ()):
                self.cookies.load(hdr)

        __headers = {}
        _headers = property(headers_getter, headers_setter)

    headers = kwargs["headers"]
    for name, value in kwargs["cookies"].items():
        headers["Set-Cookie"] = f"{name}={value}"

    return CallbackResult(
        response_class=Response,
        status=200,
        headers=headers,
        body=json.dumps(
            {
                "path_url": f"{url.path}?{url.query_string}",
                "timeout": kwargs["timeout"],
                "verify": kwargs["ssl"],
            },
        ),
    )


async def test_representation() -> None:
    driver = aiohttp_driver()
    setattr(driver, "_middleware", [])
    assert repr(driver) == "AioHttpDriver(timeout=300, verify=True)"


async def test_representation_with_middleware() -> None:
    driver = aiohttp_driver(RequestMiddleware, ResponseMiddleware)
    assert repr(driver) == (
        "AioHttpDriver("
        "Authentication, RequestMiddleware, ResponseMiddleware, "
        "timeout=300, verify=True"
        ")"
    )


async def test_string_representation() -> None:
    driver = aiohttp_driver()
    assert str(driver) == "<AsyncDriver 'aiohttp'>"


async def test_get_content(responses: aioresponses):
    responses.get("https://example.com", body="Hello, World!")
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.get_hello_world()
    assert response.status_code == 200
    assert response.content == b"Hello, World!"


async def test_get_text(responses: aioresponses):
    responses.get("https://example.com", body="Hello, World!")
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.get_hello_world()
    assert response.status_code == 200
    assert response.text() == "Hello, World!"


async def test_get_json(responses: aioresponses):
    data = {"message": "Hello, World!"}
    responses.get("https://example.com", payload=data)
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.get_hello_world()
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


async def test_headers(responses: aioresponses):
    responses.post("https://example.com", callback=echo)
    headers = {"X-Request-ID": str(uuid.uuid4())}
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.echo_headers(headers)
    assert isinstance(response.headers, CaseInsensitiveDict)
    assert response.headers["X-Request-ID"] == headers["X-Request-ID"]


async def test_query_params(responses: aioresponses):
    query_params: QueryParams = {"type": "user", "id": ["1", "2"], "name": None}
    path = "/?id=1&id=2&type=user"
    responses.get(re.compile(rf"^https://example\.com/\?{path}$"), callback=echo)
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.echo_query_params(query_params)
    assert response.json()["path_url"] == path  # type: ignore


async def test_cookies(responses: aioresponses):
    responses.get("https://example.com", callback=echo)
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
async def test_send_data(responses: aioresponses, payload):
    form_data = "name=apiwrappers&tags=api&tags=wrapper&pre-release=True&version=1"
    responses.post("https://example.com", body=form_data)
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.send_data(payload)
    assert response.text() == form_data


async def test_send_json(responses: aioresponses):
    payload = {
        "name": "apiwrappers",
        "tags": ["api", "wrapper"],
        "pre-release": True,
        "version": 1,
    }

    responses.post("https://example.com", payload=payload)
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.send_json(payload)
    assert response.json() == payload


@pytest.mark.parametrize(
    ["driver_timeout", "fetch_timeout", "timeout"],
    [
        (None, None, None),
        (None, NoValue(), None),
        (None, 0.5, 0.5),
        (300, None, None),
        (300, 1, 1),
        (300, NoValue(), 300),
    ],
)
async def test_timeout(responses: aioresponses, driver_timeout, fetch_timeout, timeout):
    responses.get("https://example.com", callback=echo)
    driver = aiohttp_driver(timeout=driver_timeout)
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = await wrapper.timeout(fetch_timeout)
    assert response.json()["timeout"] == timeout  # type: ignore


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
async def test_verify_ssl(responses: aioresponses, driver_ssl, fetch_ssl, expected):
    responses.get("https://example.com", callback=echo)
    driver = aiohttp_driver(verify=driver_ssl)
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = await wrapper.verify_ssl(fetch_ssl)
    assert response.json()["verify"] == expected  # type: ignore


@pytest.mark.parametrize(
    ["exc_name", "raised"],
    [
        ("ClientError", exceptions.DriverError),
        ("ClientConnectionError", exceptions.ConnectionFailed),
        ("ServerTimeoutError", exceptions.Timeout),
    ],
)
async def test_reraise_aiohttp_errors(responses: aioresponses, exc_name, raised):
    import aiohttp

    exc_class = getattr(aiohttp, exc_name)
    responses.get("https://example.com", exception=exc_class())
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    with pytest.raises(raised):
        await wrapper.exception()


@pytest.mark.parametrize(
    "response", [{"body": b"Plaint Text"}, {"payload": None}],
)
async def test_invalid_json_response(responses: aioresponses, response):
    responses.get("https://example.com", **response)
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    json_response = await wrapper.get_hello_world()
    with pytest.raises(json.JSONDecodeError):
        json_response.json()


async def test_middleware(responses: aioresponses):
    responses.get("https://example.com", callback=echo)
    driver = aiohttp_driver(RequestMiddleware, ResponseMiddleware)
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = await wrapper.middleware()
    assert response.headers["x-request-id"] == "request_middleware"
    assert response.headers["x-response-id"] == "response_middleware"


async def test_basic_auth(responses: aioresponses):
    responses.get("https://example.com", callback=echo)
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.basic_auth()
    assert "Basic " in response.headers["Authorization"]


async def test_token_auth(responses: aioresponses):
    responses.get("https://example.com", callback=echo)
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.token_auth()
    assert "Bearer " in response.headers["Authorization"]


async def test_complex_auth_flow(responses: aioresponses):
    responses.post("https://example.com/auth", payload={"token": "authtoken"})
    responses.get("https://example.com", callback=echo)
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.complex_auth_flow()
    assert response.headers["Authorization"] == "Bearer authtoken"
