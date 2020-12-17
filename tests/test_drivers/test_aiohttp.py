# pylint: disable=import-outside-toplevel,too-many-lines

from __future__ import annotations

import json
import ssl
from datetime import timedelta
from http.cookies import SimpleCookie
from pathlib import Path
from typing import TYPE_CHECKING, Type
from unittest import mock

import pytest

from apiwrappers import exceptions
from apiwrappers.protocols import AsyncMiddleware
from apiwrappers.structures import CaseInsensitiveDict, NoValue

from .httpbin_client import HttpBin
from .middleware import RequestMiddleware, ResponseMiddleware

if TYPE_CHECKING:
    from apiwrappers.drivers.aiohttp import AioHttpDriver


pytestmark = [pytest.mark.aiohttp, pytest.mark.asyncio]

BASE_DIR = Path(__file__).absolute().parent
INVALID_CA_BUNDLE = str(BASE_DIR.joinpath("certs/invalid-ca-bundle.crt"))
INVALID_CA_BUNDLE_PATH = str(BASE_DIR.joinpath("certs/no-ca-bundle.crt"))

CLIENT_CERT = str(BASE_DIR.joinpath("certs/client.pem"))
CLIENT_CERT_PAIR = (
    str(BASE_DIR.joinpath("certs/client.crt")),
    str(BASE_DIR.joinpath("certs/client.key")),
)


def aiohttp_driver(*middleware: Type[AsyncMiddleware], **kwargs) -> AioHttpDriver:
    from apiwrappers.drivers.aiohttp import AioHttpDriver

    kwargs.setdefault("timeout", 30)
    return AioHttpDriver(*middleware, **kwargs)


async def mock_request(*args, **kwargs):
    # pylint: disable=unused-argument
    async def read():
        return b""

    response = mock.MagicMock(read=read)
    return response


async def test_representation() -> None:
    driver = aiohttp_driver()
    setattr(driver, "_middleware", [])
    assert repr(driver) == "AioHttpDriver(timeout=30, verify=True, cert=None)"


async def test_representation_with_middleware() -> None:
    driver = aiohttp_driver(RequestMiddleware, ResponseMiddleware)
    assert repr(driver) == (
        "AioHttpDriver("
        "Authentication, RequestMiddleware, ResponseMiddleware, "
        "timeout=30, verify=True, cert=None"
        ")"
    )


async def test_representation_with_verify_and_cert() -> None:
    driver = aiohttp_driver(verify=INVALID_CA_BUNDLE, cert=CLIENT_CERT_PAIR)
    assert repr(driver) == (
        "AioHttpDriver("
        "Authentication, "
        f"timeout=30, verify='{INVALID_CA_BUNDLE}', cert={CLIENT_CERT_PAIR}"
        ")"
    )


async def test_string_representation() -> None:
    driver = aiohttp_driver()
    assert str(driver) == "<AsyncDriver 'aiohttp'>"


async def test_get_content(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=aiohttp_driver())
    response = await client.get()
    assert b"/get" in response.content
    assert response.status_code == 200


async def test_get_text(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=aiohttp_driver())
    response = await client.get()
    assert "/get" in response.text()
    assert response.status_code == 200


async def test_get_json(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=aiohttp_driver())
    response = await client.get()
    assert response.json()["url"].endswith("/get")  # type: ignore
    assert response.status_code == 200


async def test_query_params(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=aiohttp_driver())
    response = await client.get(params={"type": "user", "id": ["1", "2"], "name": None})
    assert response.json()["url"].endswith("/get?type=user&id=1&id=2")  # type: ignore


async def test_headers(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=aiohttp_driver())
    response = await client.headers({"Custom-Header": "value"})
    assert isinstance(response.headers, CaseInsensitiveDict)
    assert response.json()["headers"]["Custom-Header"] == "value"  # type: ignore


async def test_response_headers(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=aiohttp_driver())
    response = await client.response_headers({"Custom-Header": "value"})
    assert isinstance(response.headers, CaseInsensitiveDict)
    assert response.headers["Custom-Header"] == "value"


async def test_cookies_sent(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=aiohttp_driver())
    response = await client.cookies({"mycookie": "mycookievalue"})
    assert isinstance(response.cookies, SimpleCookie)
    assert "mycookie" not in response.cookies
    assert response.json()["cookies"]["mycookie"] == "mycookievalue"  # type: ignore


async def test_set_cookie(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=aiohttp_driver())
    response = await client.set_cookie("mycookie", "mycookievalue")
    assert isinstance(response.cookies, SimpleCookie)
    assert response.status_code == 200
    assert "mycookie" not in response.cookies
    # httpbin fixture works incorrectly in this case,
    # but making same request to the httpbin.org sets cookie fine
    # assert response.json()["cookies"]["mycookie"] == "mycookievalue"


@pytest.mark.parametrize(
    "payload",
    [
        {
            "name": "apiwrappers",
            "tags": ["api", "client"],
            "pre-release": True,
            "version": 1,
        },
        [
            ("name", "apiwrappers"),
            ("tags", "api"),
            ("tags", "client"),
            ("pre-release", True),
            ("version", 1),
        ],
    ],
)
async def test_send_data(httpbin, payload) -> None:
    client = HttpBin(httpbin.url, driver=aiohttp_driver())
    response = await client.post(data=payload)
    assert response.json()["form"] == {  # type: ignore
        "name": "apiwrappers",
        "tags": ["api", "client"],
        "pre-release": "True",
        "version": "1",
    }


@pytest.mark.parametrize(
    "files",
    [
        {"file": open(CLIENT_CERT, "rb")},
        {"file": ("ca-bundle", open(CLIENT_CERT, "rb"))},
        {"file": ("ca-bundle", open(CLIENT_CERT, "rb"), "text/plain")},
    ],
)
async def test_send_files(httpbin, files) -> None:
    client = HttpBin(httpbin.url, driver=aiohttp_driver())
    response = await client.post(files=files)
    line = "-----BEGIN PRIVATE KEY-----"
    assert response.json()["files"]["file"].startswith(line)  # type: ignore


async def test_send_json(httpbin) -> None:
    payload = {
        "name": "apiwrappers",
        "tags": ["api", "client"],
        "pre-release": True,
        "version": 1,
    }

    client = HttpBin(httpbin.url, driver=aiohttp_driver())
    response = await client.post(json=payload)
    assert response.json()["json"] == payload  # type: ignore


@pytest.mark.parametrize(
    ["driver_timeout", "fetch_timeout", "expected"],
    [
        (None, None, None),
        (None, NoValue(), None),
        (None, 0.5, 0.5),
        (300, None, None),
        (300, 1, 1),
        (300, NoValue(), 300),
        (timedelta(minutes=1), NoValue(), 60),
        (None, timedelta(minutes=1), 60),
    ],
)
async def test_timeout(driver_timeout, fetch_timeout, expected) -> None:
    driver = aiohttp_driver(timeout=driver_timeout)
    wrapper = HttpBin("https://httpbin.org", driver=driver)
    target = "aiohttp.client.ClientSession.request"
    with mock.patch(target, side_effect=mock_request) as request_mock:
        await wrapper.delay(2, fetch_timeout)
    _, call_kwargs = request_mock.call_args
    assert call_kwargs["timeout"] == expected


async def test_timeout_exceeds(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=aiohttp_driver())
    with pytest.raises(exceptions.Timeout):
        await client.delay(2, timeout=0.1)


async def test_verify_with_invalid_ca_bundle(httpbin_secure) -> None:
    driver = aiohttp_driver(verify=INVALID_CA_BUNDLE)
    client = HttpBin(httpbin_secure.url, driver=driver)
    with pytest.raises(ssl.SSLError) as excinfo:
        await client.get()
    assert "X509" in str(excinfo.value)
    assert "no certificate or crl found" in str(excinfo.value)


async def test_verify_with_invalid_path_to_ca_bundle(httpbin_secure) -> None:
    driver = aiohttp_driver(verify=INVALID_CA_BUNDLE_PATH)
    client = HttpBin(httpbin_secure.url, driver=driver)
    with pytest.raises(OSError) as excinfo:
        await client.get()
    assert str(excinfo.value) == (
        f"Could not find a suitable TLS CA certificate bundle, "
        f"invalid path: {INVALID_CA_BUNDLE_PATH}"
    )


async def test_verify_failure(httpbin_secure) -> None:
    client = HttpBin(httpbin_secure.url, driver=aiohttp_driver())
    with pytest.raises(ssl.SSLError) as excinfo:
        await client.get()
    assert "CERTIFICATE_VERIFY_FAILED" in str(excinfo)


async def test_verify_disabled(httpbin_secure) -> None:
    driver = aiohttp_driver(verify=False)
    client = HttpBin(httpbin_secure.url, driver=driver)
    response = await client.get()
    assert response.status_code == 200


async def test_verify_with_custom_ca_bundle(httpbin_secure, httpbin_ca_bundle) -> None:
    driver = aiohttp_driver(verify=httpbin_ca_bundle)
    client = HttpBin(httpbin_secure.url, driver=driver)
    response = await client.get()
    assert response.status_code == 200


@pytest.mark.parametrize(
    "cert", [CLIENT_CERT, CLIENT_CERT_PAIR],
)
async def test_cert(httpbin_secure, httpbin_ca_bundle, cert) -> None:
    driver = aiohttp_driver(verify=httpbin_ca_bundle, cert=cert)
    client = HttpBin(httpbin_secure.url, driver=driver)
    response = await client.get()
    assert response.status_code == 200

    target = "aiohttp.client.ClientSession.request"
    with mock.patch(target, side_effect=mock_request) as request_mock:
        await client.get()
    _, call_kwargs = request_mock.call_args
    assert call_kwargs["ssl"]


async def test_invalid_cert(httpbin_secure, httpbin_ca_bundle) -> None:
    driver = aiohttp_driver(verify=httpbin_ca_bundle, cert=INVALID_CA_BUNDLE)
    client = HttpBin(httpbin_secure.url, driver=driver)
    with pytest.raises(ssl.SSLError) as excinfo:
        await client.get()
    assert "[SSL] PEM lib" in str(excinfo.value)


async def test_invalid_path_to_cert(httpbin) -> None:
    driver = aiohttp_driver(cert=INVALID_CA_BUNDLE_PATH)
    client = HttpBin(httpbin.url, driver=driver)
    with pytest.raises(OSError) as excinfo:
        await client.get()
    assert str(excinfo.value) == (
        f"Could not find the TLS certificate file, "
        f"invalid path: {INVALID_CA_BUNDLE_PATH}"
    )


async def test_connection_failed() -> None:
    client = HttpBin("http://doesnotexist.google.com", driver=aiohttp_driver())
    with pytest.raises(exceptions.ConnectionFailed):
        await client.get()


async def test_reraise_unhandled_exceptions() -> None:
    client = HttpBin("invalid_url", driver=aiohttp_driver())
    with pytest.raises(exceptions.DriverError):
        # aiohttp raises InvalidURL
        await client.get()  # type: ignore


async def test_invalid_json_response(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=aiohttp_driver())
    response = await client.html()
    with pytest.raises(json.JSONDecodeError):
        response.json()


async def test_middleware(httpbin) -> None:
    driver = aiohttp_driver(RequestMiddleware, ResponseMiddleware)
    client = HttpBin(httpbin.url, driver=driver)
    response = await client.get()
    assert response.json()["headers"]["Request"] == "middleware"  # type: ignore
    assert "Response" not in response.json()["headers"]  # type: ignore
    assert response.headers["Response"] == "middleware"


async def test_basic_auth(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=aiohttp_driver())
    response = await client.basic_auth("admin", "root")
    assert response.json() == {
        "authenticated": True,
        "user": "admin",
    }


async def test_token_auth(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=aiohttp_driver())
    response = await client.bearer_auth("vF9dft4qmT")
    assert response.json() == {
        "authenticated": True,
        "token": "vF9dft4qmT",
    }


async def test_complex_auth_flow(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=aiohttp_driver())
    response = await client.complex_auth_flow("vF9dft4qmT")
    assert response.json() == {  # type: ignore
        "authenticated": True,
        "token": "vF9dft4qmT",
    }
