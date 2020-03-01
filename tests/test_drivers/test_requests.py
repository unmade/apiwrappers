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
from apiwrappers.protocols import Middleware
from apiwrappers.structures import CaseInsensitiveDict, NoValue

from .middleware import RequestMiddleware, ResponseMiddleware
from .wrappers import APIWrapper

if TYPE_CHECKING:
    from responses import RequestsMock
    from requests import PreparedRequest
    from apiwrappers.drivers.requests import RequestsDriver

pytestmark = [pytest.mark.requests]

BASE_DIR = Path(__file__).absolute().parent
CA_CERTS = str(BASE_DIR.joinpath("certs/ca-bundle.crt"))
INVALID_CERTS = str(BASE_DIR.joinpath("certs/invalid-ca-bundle.crt"))
INVALID_PATH_CERTS = str(BASE_DIR.joinpath("certs/no-ca-bundle.crt"))


@pytest.fixture
def responses():
    import responses

    with responses.RequestsMock() as mocked_responses:
        yield mocked_responses


def requests_driver(*middleware: Type[Middleware], **kwargs) -> RequestsDriver:
    from apiwrappers.drivers.requests import RequestsDriver

    return RequestsDriver(*middleware, **kwargs)


def echo(request: PreparedRequest):
    headers = dict(request.headers)
    if "Cookie" in request.headers:
        headers["Set-Cookie"] = request.headers["Cookie"]

    try:
        body = json.loads(request.body)  # type: ignore
    except (TypeError, ValueError):
        body = request.body

    return (
        200,
        headers,
        json.dumps({"path_url": request.path_url, "body": body}),
    )


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


def test_get_content(responses: RequestsMock):
    data = "Hello, World!"
    responses.add("GET", "https://example.com/", body=data)
    wrapper = APIWrapper("https://example.com", driver=requests_driver())
    response = wrapper.get_hello_world()
    assert response.status_code == 200
    assert response.content == data.encode()


def test_get_text(responses: RequestsMock):
    data = "Hello, World!"
    responses.add("GET", "https://example.com/", body=data)
    wrapper = APIWrapper("https://example.com", driver=requests_driver())
    response = wrapper.get_hello_world()
    assert response.status_code == 200
    assert response.text() == data


def test_get_json(responses: RequestsMock):
    data = {"message": "Hello, World!"}
    responses.add("GET", "https://example.com/", json=data)
    wrapper = APIWrapper("https://example.com", driver=requests_driver())
    response = wrapper.get_hello_world()
    assert response.status_code == 200
    assert response.json() == data


def test_headers(responses: RequestsMock):
    responses.add_callback("POST", "https://example.com", callback=echo)
    wrapper = APIWrapper("https://example.com", driver=requests_driver())
    headers = {"X-Request-ID": str(uuid.uuid4())}
    response = wrapper.echo_headers(headers=headers)
    assert isinstance(response.headers, CaseInsensitiveDict)
    assert response.headers["X-Request-ID"] == headers["X-Request-ID"]


def test_query_params(responses: RequestsMock):
    query_params: QueryParams = {"type": "user", "id": ["1", "2"], "name": None}
    path = "/?type=user&id=1&id=2"
    responses.add_callback("GET", f"https://example.com{path}", callback=echo)
    wrapper = APIWrapper("https://example.com", driver=requests_driver())
    response = wrapper.echo_query_params(query_params)
    assert response.json()["path_url"] == path  # type: ignore


def test_cookies(responses: RequestsMock):
    responses.add_callback("GET", "https://example.com", callback=echo)
    cookies = {"csrftoken": "YWxhZGRpbjpvcGVuc2VzYW1l"}
    wrapper = APIWrapper("https://example.com", driver=requests_driver())
    response = wrapper.echo_cookies(cookies)
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
def test_send_data(responses: RequestsMock, payload):
    responses.add_callback("POST", "https://example.com", callback=echo)
    form_data = "name=apiwrappers&tags=api&tags=wrapper&pre-release=True&version=1"
    wrapper = APIWrapper("https://example.com", driver=requests_driver())
    response = wrapper.send_data(payload)
    assert response.json()["body"] == form_data  # type: ignore


def test_send_json(responses: RequestsMock):
    responses.add_callback("POST", "https://example.com", callback=echo)

    payload = {
        "name": "apiwrappers",
        "tags": ["api", "wrapper"],
        "pre-release": True,
        "version": 1,
    }

    wrapper = APIWrapper("https://example.com", driver=requests_driver())
    response = wrapper.send_json(payload)
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
def test_timeout(driver_timeout, fetch_timeout, expected):
    driver = requests_driver(timeout=driver_timeout)
    wrapper = APIWrapper("https://example.com", driver=driver)
    with mock.patch("requests.request") as request_mock:
        wrapper.timeout(fetch_timeout)
    _, call_kwargs = request_mock.call_args
    assert call_kwargs["timeout"] == expected


@pytest.mark.parametrize(
    ["driver_ssl", "fetch_ssl", "expected"],
    [
        (True, True, True),
        (True, False, False),
        (False, False, False),
        (False, True, True),
        (False, NoValue(), False),
        (True, NoValue(), True),
        ("/path/to/ca-bundle.crt", NoValue(), "/path/to/ca-bundle.crt"),
    ],
)
def test_verify_ssl(driver_ssl, fetch_ssl, expected) -> None:
    driver = requests_driver(verify=driver_ssl)
    wrapper = APIWrapper("https://example.com", driver=driver)
    with mock.patch("requests.request") as request_mock:
        wrapper.verify_ssl(fetch_ssl)
    _, call_kwargs = request_mock.call_args
    assert call_kwargs["verify"] == expected


def test_verify_with_invalid_ca_bundle() -> None:
    driver = requests_driver(verify=INVALID_CERTS)
    wrapper = APIWrapper("https://example.com", driver=driver)
    with pytest.raises(ssl.SSLError) as excinfo:
        wrapper.verify_ssl(NoValue())
    assert "no certificate or crl found" in str(excinfo.value)


def test_verify_with_invalid_path_to_ca_bundle() -> None:
    driver = requests_driver(verify=INVALID_PATH_CERTS)
    wrapper = APIWrapper("https://example.com", driver=driver)
    with pytest.raises(OSError) as excinfo:
        wrapper.verify_ssl(NoValue())
    assert str(excinfo.value) == (
        f"Could not find a suitable TLS CA certificate bundle, "
        f"invalid path: {INVALID_PATH_CERTS}"
    )


@pytest.mark.parametrize(
    ["exc_name", "raised"],
    [
        ("RequestException", exceptions.DriverError),
        ("ConnectionError", exceptions.ConnectionFailed),
        ("Timeout", exceptions.Timeout),
        ("ConnectTimeout", exceptions.Timeout),
    ],
)
def test_reraise_requests_exceptions(responses: RequestsMock, exc_name, raised):
    import requests

    exc_class = getattr(requests, exc_name)
    responses.add("GET", "https://example.com", body=exc_class())
    wrapper = APIWrapper("https://example.com", driver=requests_driver())
    with pytest.raises(raised):
        wrapper.exception()


@pytest.mark.parametrize(
    "response",
    [
        {"body": b"Plaint Text"},
        {"body": b"Plaint Text", "content_type": "application/json"},
    ],
)
def test_invalid_json_response(responses: RequestsMock, response):
    responses.add("GET", "https://example.com", **response)
    wrapper = APIWrapper("https://example.com", driver=requests_driver())
    json_response = wrapper.get_hello_world()
    with pytest.raises(json.JSONDecodeError):
        json_response.json()


def test_middleware(responses: RequestsMock):
    responses.add_callback(responses.GET, "https://example.com", callback=echo)
    driver = requests_driver(RequestMiddleware, ResponseMiddleware)
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = wrapper.middleware()
    assert response.headers["x-request-id"] == "request_middleware"
    assert response.headers["x-response-id"] == "response_middleware"


def test_basic_auth(responses: RequestsMock):
    responses.add_callback(responses.GET, "https://example.com", callback=echo)
    wrapper = APIWrapper("https://example.com", driver=requests_driver())
    response = wrapper.basic_auth()
    assert "Basic " in response.headers["Authorization"]


def test_token_auth(responses: RequestsMock):
    responses.add_callback("GET", "https://example.com", callback=echo)
    wrapper = APIWrapper("https://example.com", driver=requests_driver())
    response = wrapper.token_auth()
    assert "Bearer " in response.headers["Authorization"]


def test_complex_auth_flow(responses: RequestsMock):
    data = {"token": "authtoken"}
    responses.add("POST", "https://example.com/auth", json=data)
    responses.add_callback(responses.GET, "https://example.com", callback=echo)
    wrapper = APIWrapper("https://example.com", driver=requests_driver())
    response = wrapper.complex_auth_flow()
    assert response.headers["Authorization"] == "Bearer authtoken"
