# pylint: disable=import-outside-toplevel,redefined-outer-name

from __future__ import annotations

import json
import uuid
from http.cookies import SimpleCookie
from typing import TYPE_CHECKING
from unittest import mock

import pytest

from apiwrappers import exceptions
from apiwrappers.entities import QueryParams
from apiwrappers.structures import CaseInsensitiveDict, NoValue

from .middleware import RequestMiddleware, ResponseMiddleware
from .wrappers import APIWrapper

if TYPE_CHECKING:
    from requests import PreparedRequest
    from apiwrappers.drivers.requests import RequestsDriver

pytestmark = [pytest.mark.requests]


@pytest.fixture
def responses():
    import responses

    with responses.RequestsMock() as mocked_responses:
        yield mocked_responses


@pytest.fixture
def driver():
    from apiwrappers.drivers.requests import RequestsDriver

    return RequestsDriver()


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


def test_representation(driver: RequestsDriver):
    setattr(driver, "_middleware", [])
    assert repr(driver) == "RequestsDriver(timeout=300, verify_ssl=True)"


def test_representation_with_middleware():
    from apiwrappers.drivers.requests import RequestsDriver

    driver = RequestsDriver(RequestMiddleware, ResponseMiddleware)
    assert repr(driver) == (
        "RequestsDriver("
        "Authentication, RequestMiddleware, ResponseMiddleware, "
        "timeout=300, verify_ssl=True"
        ")"
    )


def test_string_representation(driver: RequestsDriver):
    assert str(driver) == "<Driver 'requests'>"


def test_get_content(responses, driver: RequestsDriver):
    data = "Hello, World!"
    responses.add("GET", "https://example.com/", body=data)
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = wrapper.get_hello_world()
    assert response.status_code == 200
    assert response.content == data.encode()


def test_get_text(responses, driver: RequestsDriver):
    data = "Hello, World!"
    responses.add("GET", "https://example.com/", body=data)
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = wrapper.get_hello_world()
    assert response.status_code == 200
    assert response.text() == data


def test_get_json(responses, driver: RequestsDriver):
    data = {"message": "Hello, World!"}
    responses.add("GET", "https://example.com/", json=data)
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = wrapper.get_hello_world()
    assert response.status_code == 200
    assert response.json() == data


def test_headers(responses, driver: RequestsDriver):
    responses.add_callback("POST", "https://example.com", callback=echo)
    wrapper = APIWrapper("https://example.com", driver=driver)
    headers = {"X-Request-ID": str(uuid.uuid4())}
    response = wrapper.echo_headers(headers=headers)
    assert isinstance(response.headers, CaseInsensitiveDict)
    assert response.headers["X-Request-ID"] == headers["X-Request-ID"]


def test_query_params(responses, driver: RequestsDriver):
    query_params: QueryParams = {"type": "user", "id": ["1", "2"], "name": None}
    path = "/?type=user&id=1&id=2"
    responses.add_callback("GET", f"https://example.com{path}", callback=echo)
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = wrapper.echo_query_params(query_params)
    assert response.json()["path_url"] == path  # type: ignore


def test_cookies(responses, driver: RequestsDriver):
    responses.add_callback("GET", "https://example.com", callback=echo)
    cookies = {"csrftoken": "YWxhZGRpbjpvcGVuc2VzYW1l"}
    wrapper = APIWrapper("https://example.com", driver=driver)
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
def test_send_data_as_dict(responses, driver: RequestsDriver, payload):
    responses.add_callback("POST", "https://example.com", callback=echo)
    form_data = "name=apiwrappers&tags=api&tags=wrapper&pre-release=True&version=1"
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = wrapper.send_data(payload)
    assert response.json()["body"] == form_data  # type: ignore


def test_send_json(responses, driver: RequestsDriver):
    responses.add_callback("POST", "https://example.com", callback=echo)

    payload = {
        "name": "apiwrappers",
        "tags": ["api", "wrapper"],
        "pre-release": True,
        "version": 1,
    }

    wrapper = APIWrapper("https://example.com", driver=driver)
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
def test_timeout(driver: RequestsDriver, driver_timeout, fetch_timeout, expected):
    driver.timeout = driver_timeout
    wrapper = APIWrapper("https://example.com", driver=driver)
    with mock.patch("requests.request") as request_mock:
        wrapper.timeout(fetch_timeout)
    _, call_kwargs = request_mock.call_args
    assert call_kwargs["timeout"] == expected


def test_no_timeout(driver: RequestsDriver):
    driver.timeout = None
    wrapper = APIWrapper("https://example.com", driver=driver)
    with mock.patch("requests.request") as request_mock:
        wrapper.timeout(None)
    _, call_kwargs = request_mock.call_args
    assert call_kwargs["timeout"] is None


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
def test_verify_ssl(driver: RequestsDriver, driver_ssl, fetch_ssl, expected):
    driver.verify_ssl = driver_ssl
    wrapper = APIWrapper("https://example.com", driver=driver)
    with mock.patch("requests.request") as request_mock:
        wrapper.verify_ssl(fetch_ssl)
    _, call_kwargs = request_mock.call_args
    assert call_kwargs["verify"] == expected


@pytest.mark.parametrize(
    ["exc", "raised"],
    [
        ("RequestException", exceptions.DriverError),
        ("ConnectionError", exceptions.ConnectionFailed),
        ("Timeout", exceptions.Timeout),
        ("ConnectTimeout", exceptions.Timeout),
    ],
)
def test_reraise_requests_exceptions(responses, driver: RequestsDriver, exc, raised):
    import requests

    exc_class = getattr(requests, exc)
    responses.add("GET", "https://example.com", body=exc_class())
    wrapper = APIWrapper("https://example.com", driver=driver)
    with pytest.raises(raised):
        wrapper.exception()


@pytest.mark.parametrize(
    "response",
    [
        {"body": b"Plaint Text"},
        {"body": b"Plaint Text", "content_type": "application/json"},
    ],
)
def test_invalid_json_response(responses, driver: RequestsDriver, response):
    responses.add("GET", "https://example.com", **response)
    wrapper = APIWrapper("https://example.com", driver=driver)
    json_response = wrapper.get_hello_world()
    with pytest.raises(json.JSONDecodeError):
        json_response.json()


def test_middleware(responses) -> None:
    from apiwrappers.drivers.requests import RequestsDriver

    responses.add_callback(responses.GET, "https://example.com", callback=echo)
    driver = RequestsDriver(RequestMiddleware, ResponseMiddleware)
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = wrapper.middleware()
    assert response.headers["x-request-id"] == "request_middleware"
    assert response.headers["x-response-id"] == "response_middleware"


def test_basic_auth(responses, driver: RequestsDriver):
    responses.add_callback(responses.GET, "https://example.com", callback=echo)
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = wrapper.basic_auth()
    assert "Basic " in response.headers["Authorization"]


def test_token_auth(responses, driver: RequestsDriver):
    responses.add_callback("GET", "https://example.com", callback=echo)
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = wrapper.token_auth()
    assert "Bearer " in response.headers["Authorization"]


def test_complex_auth_flow(responses, driver: RequestsDriver):
    data = {"token": "authtoken"}
    responses.add("POST", "https://example.com/auth", json=data)
    responses.add_callback(responses.GET, "https://example.com", callback=echo)
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = wrapper.complex_auth_flow()
    assert response.headers["Authorization"] == "Bearer authtoken"
