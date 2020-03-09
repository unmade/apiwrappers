# pylint: disable=import-outside-toplevel,redefined-outer-name,too-many-lines

from __future__ import annotations

import json
import ssl
import uuid
from http.cookies import SimpleCookie
from pathlib import Path
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
    from aresponses import ResponsesMockServer as ResponsesMock
    from apiwrappers.drivers.aiohttp import AioHttpDriver


pytestmark = [pytest.mark.aiohttp, pytest.mark.asyncio]

BASE_DIR = Path(__file__).absolute().parent
CA_BUNDLE = str(BASE_DIR.joinpath("certs/ca-bundle.crt"))
INVALID_CA_BUNDLE = str(BASE_DIR.joinpath("certs/invalid-ca-bundle.crt"))
INVALID_CA_BUNDLE_PATH = str(BASE_DIR.joinpath("certs/no-ca-bundle.crt"))

CLIENT_CERT = str(BASE_DIR.joinpath("certs/client.pem"))
CLIENT_CERT_PAIR = (
    str(BASE_DIR.joinpath("certs/client.crt")),
    str(BASE_DIR.joinpath("certs/client.key")),
)


def aiohttp_driver(*middleware: Type[AsyncMiddleware], **kwargs) -> AioHttpDriver:
    from apiwrappers.drivers.aiohttp import AioHttpDriver

    return AioHttpDriver(*middleware, **kwargs)


async def mock_request(*args, **kwargs):
    # pylint: disable=unused-argument
    async def read():
        return b""

    response = mock.MagicMock(read=read)
    return response


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
    assert repr(driver) == "AioHttpDriver(timeout=300, verify=True, cert=None)"


async def test_representation_with_middleware() -> None:
    driver = aiohttp_driver(RequestMiddleware, ResponseMiddleware)
    assert repr(driver) == (
        "AioHttpDriver("
        "Authentication, RequestMiddleware, ResponseMiddleware, "
        "timeout=300, verify=True, cert=None"
        ")"
    )


async def test_representation_with_verify_and_cert() -> None:
    driver = aiohttp_driver(verify=CA_BUNDLE, cert=CLIENT_CERT_PAIR)
    assert repr(driver) == (
        "AioHttpDriver("
        "Authentication, "
        f"timeout=300, verify='{CA_BUNDLE}', cert={CLIENT_CERT_PAIR}"
        ")"
    )


async def test_string_representation() -> None:
    driver = aiohttp_driver()
    assert str(driver) == "<AsyncDriver 'aiohttp'>"


async def test_get_content(aresponses: ResponsesMock):
    aresponses.add("example.com", "/", "GET", "Hello, World!")
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.get_hello_world()
    assert response.status_code == 200
    assert response.content == b"Hello, World!"


async def test_get_text(aresponses: ResponsesMock):
    aresponses.add("example.com", "/", "GET", "Hello, World!")
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.get_hello_world()
    assert response.status_code == 200
    assert response.text() == "Hello, World!"


async def test_get_json(aresponses: ResponsesMock):
    response_mock = aresponses.Response(
        body=b'{"message": "Hello, World!"}', content_type="application/json"
    )
    aresponses.add("example.com", "/", "GET", response_mock)
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.get_hello_world()
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


async def test_headers(aresponses: ResponsesMock):
    aresponses.add("example.com", "/", "POST", echo)
    headers = {"X-Request-ID": str(uuid.uuid4())}
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.echo_headers(headers)
    assert isinstance(response.headers, CaseInsensitiveDict)
    assert response.headers["X-Request-ID"] == headers["X-Request-ID"]


async def test_query_params(aresponses: ResponsesMock):
    query_params: QueryParams = {"type": "user", "id": ["1", "2"], "name": None}
    path = "/?type=user&id=1&id=2"
    aresponses.add("example.com", path, "GET", echo, match_querystring=True)
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.echo_query_params(query_params)
    assert response.json()["path_url"] == path  # type: ignore


async def test_cookies(aresponses: ResponsesMock):
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
async def test_send_data(aresponses: ResponsesMock, payload):
    form_data = "name=apiwrappers&tags=api&tags=wrapper&pre-release=True&version=1"
    aresponses.add("example.com", "/", "POST", echo)
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.send_data(payload)
    assert response.json()["body"] == form_data  # type: ignore


@pytest.mark.parametrize(
    ["files", "filename", "has_content_type"],
    [
        ({"file": open(CA_BUNDLE, "rb")}, "ca-bundle.crt", False),
        ({"file": ("ca-bundle", open(CA_BUNDLE, "rb"))}, "ca-bundle", False),
        (
            {"file": ("ca-bundle", open(CA_BUNDLE, "rb"), "text/plain")},
            "ca-bundle",
            True,
        ),
    ],
)
async def test_send_files(aresponses: ResponsesMock, files, filename, has_content_type):
    aresponses.add("example.com", "/", "POST", echo)
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.send_files(files)
    content = response.json()["body"]  # type: ignore
    disposition = f'Content-Disposition: form-data; name="file"; filename="{filename}"'
    assert disposition in content
    assert ("Content-Type: text/plain" in content) is has_content_type


async def test_send_json(aresponses: ResponsesMock):
    payload = {
        "name": "apiwrappers",
        "tags": ["api", "wrapper"],
        "pre-release": True,
        "version": 1,
    }

    aresponses.add("example.com", "/", "POST", echo)
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.send_json(payload)
    assert response.json()["body"] == payload  # type: ignore


@pytest.mark.parametrize(
    ["driver_timeout", "fetch_timeout", "expected"],
    [
        (None, None, None),
        (None, NoValue(), None),
        (None, 0.5, 0.5),
        (300, None, None),
        (300, 1, 1),
        (300, NoValue(), 300),
    ],
)
async def test_timeout(driver_timeout, fetch_timeout, expected) -> None:
    driver = aiohttp_driver(timeout=driver_timeout)
    wrapper = APIWrapper("https://example.com", driver=driver)
    target = "aiohttp.client.ClientSession.request"
    with mock.patch(target, side_effect=mock_request) as request_mock:
        await wrapper.timeout(fetch_timeout)
    _, call_kwargs = request_mock.call_args
    assert call_kwargs["timeout"] == expected


@pytest.mark.parametrize(
    "verify,verify_mode",
    [
        (True, ssl.CERT_REQUIRED),
        (False, ssl.CERT_NONE),
        (CA_BUNDLE, ssl.CERT_REQUIRED),
    ],
)
async def test_verify(verify, verify_mode) -> None:
    driver = aiohttp_driver(verify=verify)
    wrapper = APIWrapper("https://example.com", driver=driver)
    target = "aiohttp.client.ClientSession.request"
    with mock.patch(target, side_effect=mock_request) as request_mock:
        await wrapper.verify()
    _, call_kwargs = request_mock.call_args
    assert call_kwargs["ssl"].verify_mode == verify_mode


async def test_verify_with_invalid_ca_bundle() -> None:
    driver = aiohttp_driver(verify=INVALID_CA_BUNDLE)
    wrapper = APIWrapper("https://example.com", driver=driver)
    with pytest.raises(ssl.SSLError) as excinfo:
        await wrapper.verify()
    assert "no certificate or crl found" in str(excinfo.value)


async def test_verify_with_invalid_path_to_ca_bundle() -> None:
    driver = aiohttp_driver(verify=INVALID_CA_BUNDLE_PATH)
    wrapper = APIWrapper("https://example.com", driver=driver)
    with pytest.raises(OSError) as excinfo:
        await wrapper.verify()
    assert str(excinfo.value) == (
        f"Could not find a suitable TLS CA certificate bundle, "
        f"invalid path: {INVALID_CA_BUNDLE_PATH}"
    )


@pytest.mark.parametrize(
    "cert", [CLIENT_CERT, CLIENT_CERT_PAIR],
)
async def test_cert(cert) -> None:
    driver = aiohttp_driver(cert=cert)
    wrapper = APIWrapper("https://example.com", driver=driver)
    target = "aiohttp.client.ClientSession.request"
    with mock.patch(target, side_effect=mock_request) as request_mock:
        await wrapper.verify()
    _, call_kwargs = request_mock.call_args
    assert call_kwargs["ssl"]


async def test_invalid_cert() -> None:
    driver = aiohttp_driver(cert=INVALID_CA_BUNDLE)
    wrapper = APIWrapper("https://example.com", driver=driver)
    with pytest.raises(ssl.SSLError) as excinfo:
        await wrapper.cert()
    assert "[SSL] PEM lib" in str(excinfo.value)


async def test_invalid_path_to_cert() -> None:
    driver = aiohttp_driver(cert=INVALID_CA_BUNDLE_PATH)
    wrapper = APIWrapper("https://example.com", driver=driver)
    with pytest.raises(OSError) as excinfo:
        await wrapper.cert()
    assert str(excinfo.value) == (
        f"Could not find the TLS certificate file, "
        f"invalid path: {INVALID_CA_BUNDLE_PATH}"
    )


@pytest.mark.parametrize(
    ["exc_name", "raised"],
    [
        ("ClientError", exceptions.DriverError),
        ("ClientConnectionError", exceptions.ConnectionFailed),
        ("ServerTimeoutError", exceptions.Timeout),
    ],
)
async def test_reraise_aiohttp_errors(exc_name, raised) -> None:
    import aiohttp

    exc_class = getattr(aiohttp, exc_name)
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    target = "aiohttp.client.ClientSession.request"
    with mock.patch(target, side_effect=exc_class()), pytest.raises(raised):
        await wrapper.exception()


@pytest.mark.parametrize(
    "response",
    [
        {"body": b"Plaint Text"},
        {"body": b"Plaint Text", "content_type": "application/json"},
    ],
)
async def test_invalid_json_response(aresponses: ResponsesMock, response):
    aresponses.add("example.com", "/", "GET", aresponses.Response(**response))
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    json_response = await wrapper.get_hello_world()
    with pytest.raises(json.JSONDecodeError):
        json_response.json()


async def test_middleware(aresponses: ResponsesMock):
    aresponses.add("example.com", "/", "GET", echo)
    driver = aiohttp_driver(RequestMiddleware, ResponseMiddleware)
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = await wrapper.middleware()
    assert response.headers["x-request-id"] == "request_middleware"
    assert response.headers["x-response-id"] == "response_middleware"


async def test_basic_auth(aresponses: ResponsesMock):
    aresponses.add("example.com", "/", "GET", echo)
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.basic_auth()
    assert "Basic " in response.headers["Authorization"]


async def test_token_auth(aresponses: ResponsesMock):
    aresponses.add("example.com", "/", "GET", echo)
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.token_auth()
    assert "Bearer " in response.headers["Authorization"]


async def test_complex_auth_flow(aresponses: ResponsesMock):
    token_payload = aresponses.Response(
        body=b'{"token": "authtoken"}', content_type="application/json"
    )
    aresponses.add("example.com", "/auth", "POST", token_payload)
    aresponses.add("example.com", "/", "GET", echo)
    wrapper = APIWrapper("https://example.com", driver=aiohttp_driver())
    response = await wrapper.complex_auth_flow()
    assert response.headers["Authorization"] == "Bearer authtoken"
