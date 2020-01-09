# pylint: disable=import-outside-toplevel,redefined-outer-name

import uuid
from http.cookies import SimpleCookie
from typing import TYPE_CHECKING
from unittest import mock

import pytest

from apiwrappers.entities import QueryParams
from apiwrappers.structures import CaseInsensitiveDict
from apiwrappers.utils import NoValue

from .wrappers import APIWrapper

if TYPE_CHECKING:
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


def test_get_content(responses, driver: "RequestsDriver"):
    responses.add(
        "GET", "https://example.com/", body="Hello, World!",
    )
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = wrapper.get_hello_world()
    assert response.status_code == 200
    assert response.content == b"Hello, World!"


def test_get_text(responses, driver: "RequestsDriver"):
    responses.add(
        "GET", "https://example.com/", body="Hello, World!",
    )
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = wrapper.get_hello_world()
    assert response.status_code == 200
    assert response.text() == "Hello, World!"


def test_get_json(responses, driver: "RequestsDriver"):
    responses.add(
        "GET", "https://example.com/", json={"message": "Hello, World!"},
    )
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = wrapper.get_hello_world()
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


def test_headers(responses, driver: "RequestsDriver"):
    def echo_headers(request):
        headers = {"X-Response-ID": request.headers["x-request-id"]}
        return (200, headers, '{"code": 200, "message": "ok"}')

    responses.add_callback(
        responses.POST, "https://example.com", callback=echo_headers,
    )

    wrapper = APIWrapper("https://example.com", driver=driver)
    headers = {"X-Request-ID": str(uuid.uuid4())}
    response = wrapper.echo_headers(headers=headers)
    assert isinstance(response.headers, CaseInsensitiveDict)
    assert response.headers["X-Response-ID"] == headers["X-Request-ID"]


def test_query_params(responses, driver: "RequestsDriver"):
    def echo_url_path(request):
        return (200, {}, request.path_url)

    query_params: QueryParams = {"type": "user", "id": ["1", "2"], "name": None}
    path = "/?type=user&id=1&id=2"
    responses.add_callback("GET", f"https://example.com{path}", callback=echo_url_path)

    wrapper = APIWrapper("https://example.com", driver=driver)
    response = wrapper.echo_query_params(query_params)
    assert response.text() == path


def test_cookies(responses, driver: "RequestsDriver"):
    def echo_cookies(request):
        return (200, {"Set-Cookie": request.headers["Cookie"]}, "")

    responses.add_callback("GET", "https://example.com", callback=echo_cookies)

    cookies = {"csrftoken": "YWxhZGRpbjpvcGVuc2VzYW1l"}
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = wrapper.echo_cookies(cookies)
    assert isinstance(response.cookies, SimpleCookie)
    assert response.cookies["csrftoken"].value == cookies["csrftoken"]


def test_send_data_as_dict(responses, driver: "RequestsDriver"):
    def echo_data(request):
        return (200, {}, request.body)

    responses.add_callback("POST", "https://example.com", callback=echo_data)

    payload = {
        "name": "apiwrappers",
        "tags": ["api", "wrapper"],
        "pre-release": True,
        "version": 1,
    }
    form_data = "name=apiwrappers&tags=api&tags=wrapper&pre-release=True&version=1"
    wrapper = APIWrapper("https://example.com", driver=driver)

    response = wrapper.send_data(payload)
    assert response.text() == form_data


def test_send_data_as_tuples(responses, driver: "RequestsDriver"):
    def echo_data(request):
        return (200, {}, request.body)

    responses.add_callback("POST", "https://example.com", callback=echo_data)

    payload = [
        ("name", "apiwrappers"),
        ("tags", "api"),
        ("tags", "wrapper"),
        ("pre-release", True),
        ("version", 1),
    ]
    form_data = "name=apiwrappers&tags=api&tags=wrapper&pre-release=True&version=1"
    wrapper = APIWrapper("https://example.com", driver=driver)

    response = wrapper.send_data(payload)
    assert response.text() == form_data


def test_send_json(responses, driver: "RequestsDriver"):
    def echo_data(request):
        return (200, {}, request.body)

    responses.add_callback("POST", "https://example.com", callback=echo_data)

    payload = {
        "name": "apiwrappers",
        "tags": ["api", "wrapper"],
        "pre-release": True,
        "version": 1,
    }

    wrapper = APIWrapper("https://example.com", driver=driver)
    response = wrapper.send_json(payload)
    assert response.json() == payload


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
def test_timeout(driver: "RequestsDriver", driver_timeout, fetch_timeout, expected):
    driver.timeout = driver_timeout
    wrapper = APIWrapper("https://example.com", driver=driver)
    with mock.patch("requests.request") as request_mock:
        wrapper.timeout(fetch_timeout)
    _, call_kwargs = request_mock.call_args
    assert call_kwargs["timeout"] == expected


def test_no_timeout(driver: "RequestsDriver"):
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
def test_verify_ssl(driver: "RequestsDriver", driver_ssl, fetch_ssl, expected):
    driver.verify_ssl = driver_ssl
    wrapper = APIWrapper("https://example.com", driver=driver)
    with mock.patch("requests.request") as request_mock:
        wrapper.verify_ssl(fetch_ssl)
    _, call_kwargs = request_mock.call_args
    assert call_kwargs["verify"] == expected
