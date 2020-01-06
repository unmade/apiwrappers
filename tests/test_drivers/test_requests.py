# pylint: disable=import-outside-toplevel,redefined-outer-name

import uuid

import pytest

from apiwrappers.structures import CaseInsensitiveDict

from .wrappers import APIWrapper

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


def test_get_text(responses, driver):
    responses.add(
        "GET", "https://example.com/", body="Hello, World!",
    )
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = wrapper.get_hello_world()
    assert response.status_code == 200
    assert response.text() == "Hello, World!"


def test_get_json(responses, driver):
    responses.add(
        "GET", "https://example.com/", json={"message": "Hello, World!"},
    )
    wrapper = APIWrapper("https://example.com", driver=driver)
    response = wrapper.get_hello_world()
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


def test_headers(responses, driver):
    def request_callback(request):
        headers = {"X-Response-ID": request.headers["x-request-id"]}
        return (200, headers, '{"code": 200, "message": "ok"}')

    responses.add_callback(
        responses.POST, "https://example.com", callback=request_callback,
    )

    wrapper = APIWrapper("https://example.com", driver=driver)
    headers = {"X-Request-ID": str(uuid.uuid4())}
    response = wrapper.echo_headers(headers=headers)
    assert isinstance(response.headers, CaseInsensitiveDict)
    assert response.headers["X-Response-ID"] == headers["X-Request-ID"]
