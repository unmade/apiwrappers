import pytest

from apiwrappers.entities import Method, Request, Response
from apiwrappers.middleware import BaseMiddleware
from apiwrappers.middleware.auth import Authorization

from .. import factories


class First(BaseMiddleware):
    def process_request(self, request: Request) -> Request:
        request.headers = {"x-request-id": "1"}
        return super().process_request(request)

    def process_response(self, response: Response) -> Response:
        response.headers["x-response-id"] += "1"
        return response


class Second(BaseMiddleware):
    def process_request(self, request: Request) -> Request:
        request.headers["x-request-id"] += "2"  # type: ignore
        return super().process_request(request)

    def process_response(self, response: Response) -> Response:
        response.headers["x-response-id"] = "2"
        return response


def test_chain_on_instance_access() -> None:
    response = factories.make_response(b"")
    driver = factories.make_driver(response)
    assert driver.middleware == [Authorization]


def test_chain_on_class_access() -> None:
    driver_cls = factories.DriverMock
    assert driver_cls.middleware == [Authorization]
    assert driver_cls.middleware is driver_cls.middleware


def test_chain_on_instance_access_before_set() -> None:
    response = factories.make_response(b"")
    driver = factories.DriverMock(response)
    assert driver.middleware == [Authorization]

    driver.middleware.append(BaseMiddleware)
    assert driver.middleware == [Authorization, BaseMiddleware]


def test_chain_returns_different_objects_on_instance_and_class_access() -> None:
    response = factories.make_response(b"")
    driver = factories.DriverMock(response)
    assert driver.middleware is not factories.DriverMock.middleware


def test_chain_on_instance_set() -> None:
    response = factories.make_response(b"")
    driver = factories.make_driver(response)
    driver.middleware = [BaseMiddleware]
    assert driver.middleware == [Authorization, BaseMiddleware]


def test_chain_order_of_execution() -> None:
    response_mock = factories.make_response(b"")
    driver = factories.make_driver(response_mock, First, Second)
    response = driver.fetch(Request(Method.GET, "", ""))
    assert response.request.headers["x-request-id"] == "12"
    assert response.headers["x-response-id"] == "21"


@pytest.mark.asyncio
async def test_chain_order_of_execution_async_driver() -> None:
    response_mock = factories.make_response(b"")
    driver = factories.make_async_driver(response_mock, First, Second)
    response = await driver.fetch(Request(Method.GET, "", ""))
    assert response.request.headers["x-request-id"] == "12"
    assert response.headers["x-response-id"] == "21"
