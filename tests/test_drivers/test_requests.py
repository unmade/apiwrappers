# pylint: disable=import-outside-toplevel,redefined-outer-name

import pytest

from apiwrappers import Method, Request

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


def test_driver_fetch_content(responses, driver):
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
