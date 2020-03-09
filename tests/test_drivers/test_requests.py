# pylint: disable=import-outside-toplevel,too-many-lines

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
from apiwrappers.protocols import Middleware
from apiwrappers.structures import CaseInsensitiveDict, NoValue

from .httpbin_client import HttpBin
from .middleware import RequestMiddleware, ResponseMiddleware

if TYPE_CHECKING:
    from apiwrappers.drivers.requests import RequestsDriver

pytestmark = [pytest.mark.requests]

BASE_DIR = Path(__file__).absolute().parent
INVALID_CA_BUNDLE = str(BASE_DIR.joinpath("certs/invalid-ca-bundle.crt"))
INVALID_CA_BUNDLE_PATH = str(BASE_DIR.joinpath("certs/no-ca-bundle.crt"))

CLIENT_CERT = str(BASE_DIR.joinpath("certs/client.pem"))
CLIENT_CERT_PAIR = (
    str(BASE_DIR.joinpath("certs/client.crt")),
    str(BASE_DIR.joinpath("certs/client.key")),
)


def requests_driver(*middleware: Type[Middleware], **kwargs) -> RequestsDriver:
    from apiwrappers.drivers.requests import RequestsDriver

    return RequestsDriver(*middleware, **kwargs)


def test_representation() -> None:
    driver = requests_driver()
    setattr(driver, "_middleware", [])
    assert repr(driver) == "RequestsDriver(timeout=300, verify=True)"


def test_representation_with_middleware() -> None:
    driver = requests_driver(RequestMiddleware, ResponseMiddleware)
    assert repr(driver) == (
        "RequestsDriver("
        "Authentication, RequestMiddleware, ResponseMiddleware, "
        "timeout=300, verify=True"
        ")"
    )


def test_string_representation() -> None:
    driver = requests_driver()
    assert str(driver) == "<Driver 'requests'>"


def test_get_content(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=requests_driver())
    response = client.get()
    assert b"/get" in response.content
    assert response.status_code == 200


def test_get_text(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=requests_driver())
    response = client.get()
    assert "/get" in response.text()
    assert response.status_code == 200


def test_get_json(httpbin) -> None:
    client = HttpBin(str(httpbin.url), driver=requests_driver())
    response = client.get()
    assert response.json()["url"].endswith("/get")  # type: ignore
    assert response.status_code == 200


def test_query_params(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=requests_driver())
    response = client.get(params={"type": "user", "id": ["1", "2"], "name": None})
    assert response.json()["url"].endswith("/get?type=user&id=1&id=2")  # type: ignore


def test_headers(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=requests_driver())
    response = client.headers({"Custom-Header": "value"})
    assert isinstance(response.headers, CaseInsensitiveDict)
    assert response.json()["headers"]["Custom-Header"] == "value"  # type: ignore


def test_response_headers(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=requests_driver())
    response = client.response_headers({"Custom-Header": "value"})
    assert isinstance(response.headers, CaseInsensitiveDict)
    assert response.headers["Custom-Header"] == "value"


def test_cookies_sent(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=requests_driver())
    response = client.cookies({"mycookie": "mycookievalue"})
    assert isinstance(response.cookies, SimpleCookie)
    assert "mycookie" not in response.cookies
    assert response.json()["cookies"]["mycookie"] == "mycookievalue"  # type: ignore


def test_set_cookie(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=requests_driver())
    response = client.set_cookie("mycookie", "mycookievalue")
    assert isinstance(response.cookies, SimpleCookie)
    assert "mycookie" not in response.cookies
    assert response.json()["cookies"]["mycookie"] == "mycookievalue"  # type: ignore


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
def test_send_data(httpbin, payload) -> None:
    client = HttpBin(httpbin.url, driver=requests_driver())
    response = client.post(data=payload)
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
def test_send_files(httpbin, files) -> None:
    client = HttpBin(httpbin.url, driver=requests_driver())
    response = client.post(files=files)
    line = "-----BEGIN PRIVATE KEY-----"
    assert response.json()["files"]["file"].startswith(line)  # type: ignore


def test_send_json(httpbin) -> None:
    payload = {
        "name": "apiwrappers",
        "tags": ["api", "client"],
        "pre-release": True,
        "version": 1,
    }

    client = HttpBin(httpbin.url, driver=requests_driver())
    response = client.post(json=payload)
    assert response.json()["json"] == payload  # type: ignore


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
def test_timeout(driver_timeout, fetch_timeout, expected):
    driver = requests_driver(timeout=driver_timeout)
    client = HttpBin("https://httpbin.org", driver=driver)
    with mock.patch("requests.request") as request_mock:
        client.delay(2, timeout=fetch_timeout)
    _, call_kwargs = request_mock.call_args
    assert call_kwargs["timeout"] == expected


def test_timeout_exceeds(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=requests_driver())
    with pytest.raises(exceptions.Timeout):
        client.delay(1, timeout=0.1)


def test_verify_with_invalid_ca_bundle(httpbin_secure) -> None:
    driver = requests_driver(verify=INVALID_CA_BUNDLE)
    client = HttpBin(httpbin_secure.url, driver=driver)
    with pytest.raises(ssl.SSLError) as excinfo:
        client.get()
    assert "[X509] no certificate or crl found" in str(excinfo.value)


def test_verify_with_invalid_path_to_ca_bundle(httpbin_secure) -> None:
    driver = requests_driver(verify=INVALID_CA_BUNDLE_PATH)
    client = HttpBin(httpbin_secure.url, driver=driver)
    with pytest.raises(OSError) as excinfo:
        client.get()
    assert str(excinfo.value) == (
        f"Could not find a suitable TLS CA certificate bundle, "
        f"invalid path: {INVALID_CA_BUNDLE_PATH}"
    )


def test_verify_failure(httpbin_secure) -> None:
    client = HttpBin(httpbin_secure.url, driver=requests_driver())
    with pytest.raises(ssl.SSLError) as excinfo:
        client.get()
    assert "CERTIFICATE_VERIFY_FAILED" in str(excinfo)


def test_verify_disabled(httpbin_secure) -> None:
    from urllib3.exceptions import InsecureRequestWarning

    driver = requests_driver(verify=False)
    client = HttpBin(httpbin_secure.url, driver=driver)
    with pytest.warns(InsecureRequestWarning):
        response = client.get()
    assert response.status_code == 200


def test_verify_with_custom_ca_bundle(httpbin_secure, httpbin_ca_bundle) -> None:
    driver = requests_driver(verify=httpbin_ca_bundle)
    client = HttpBin(httpbin_secure.url, driver=driver)
    response = client.get()
    assert response.status_code == 200


@pytest.mark.parametrize(
    "cert", [CLIENT_CERT, CLIENT_CERT_PAIR],
)
def test_cert(httpbin_secure, httpbin_ca_bundle, cert) -> None:
    driver = requests_driver(verify=httpbin_ca_bundle, cert=cert)
    client = HttpBin(httpbin_secure.url, driver=driver)
    response = client.get()
    assert response.status_code == 200

    with mock.patch("requests.request") as request_mock:
        client.get()
    _, call_kwargs = request_mock.call_args
    assert call_kwargs["cert"] == cert


def test_invalid_cert(httpbin_secure, httpbin_ca_bundle) -> None:
    driver = requests_driver(verify=httpbin_ca_bundle, cert=INVALID_CA_BUNDLE)
    client = HttpBin(httpbin_secure.url, driver=driver)
    with pytest.raises(ssl.SSLError) as excinfo:
        client.get()
    assert "[SSL] PEM lib" in str(excinfo.value)


def test_invalid_path_to_cert(httpbin) -> None:
    driver = requests_driver(cert=INVALID_CA_BUNDLE_PATH)
    client = HttpBin(httpbin.url, driver=driver)
    with pytest.raises(OSError) as excinfo:
        client.get()
    assert str(excinfo.value) == (
        f"Could not find the TLS certificate file, "
        f"invalid path: {INVALID_CA_BUNDLE_PATH}"
    )


def test_connection_failed() -> None:
    client = HttpBin("http://doesnotexist.google.com", driver=requests_driver())
    with pytest.raises(exceptions.ConnectionFailed):
        client.get()


def test_reraise_unhandled_exceptions(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=requests_driver())
    with pytest.raises(exceptions.DriverError):
        # requests raises InvalidHeader
        client.headers({"Tags": ["api", "client"]})  # type: ignore


def test_invalid_json_response(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=requests_driver())
    response = client.html()
    with pytest.raises(json.JSONDecodeError):
        response.json()


def test_middleware(httpbin) -> None:
    driver = requests_driver(RequestMiddleware, ResponseMiddleware)
    client = HttpBin(httpbin.url, driver=driver)
    response = client.get()
    assert response.json()["headers"]["Request"] == "middleware"  # type: ignore
    assert "Response" not in response.json()["headers"]  # type: ignore
    assert response.headers["Response"] == "middleware"


def test_basic_auth(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=requests_driver())
    response = client.basic_auth("admin", "root")
    assert response.json() == {
        "authenticated": True,
        "user": "admin",
    }


def test_token_auth(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=requests_driver())
    response = client.bearer_auth("vF9dft4qmT")
    assert response.json() == {
        "authenticated": True,
        "token": "vF9dft4qmT",
    }


def test_complex_auth_flow(httpbin) -> None:
    client = HttpBin(httpbin.url, driver=requests_driver())
    response = client.complex_auth_flow()
    assert response.json()["authenticated"] is True  # type: ignore
    assert uuid.UUID(response.json()["token"])  # type: ignore
