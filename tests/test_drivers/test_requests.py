# pylint: disable=import-outside-toplevel,redefined-outer-name

import uuid

import pytest

from apiwrappers import Method, Request
from apiwrappers.structures import CaseInsensitiveDict

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


def test_fetch(responses, driver):
    responses.add(
        "POST",
        "https://example.com/users",
        body='{"code": 200, "message": "ok"}',
        status=200,
        content_type="application/json",
    )
    request = Request(
        Method.POST, "https://example.com", "/users", json={"foo": "bar"},
    )
    response = driver.fetch(request)
    assert response.status_code == 200
    assert response.text() == '{"code": 200, "message": "ok"}'
    assert response.json() == {"code": 200, "message": "ok"}


def test_headers(responses, driver):
    def request_callback(request):
        headers = {"X-Response-ID": request.headers["x-request-id"]}
        return (200, headers, '{"code": 200, "message": "ok"}')

    responses.add_callback(
        responses.POST, "https://example.com", callback=request_callback,
    )
    request = Request(
        Method.POST,
        "https://example.com",
        "/",
        headers={"X-Request-ID": str(uuid.uuid4())},
    )
    response = driver.fetch(request)
    assert isinstance(response.headers, CaseInsensitiveDict)
    assert response.headers["X-Response-ID"] == request.headers["X-Request-ID"]
