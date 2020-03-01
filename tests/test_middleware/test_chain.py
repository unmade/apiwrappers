from unittest import mock

import pytest

from apiwrappers.entities import Method, Request, Response
from apiwrappers.middleware import BaseMiddleware, MiddlewareChain

from .. import factories


class First(BaseMiddleware):
    def process_request(self, request: Request) -> Request:
        request.headers["x-request-id"] = "1"
        return super().process_request(request)

    def process_response(self, response: Response) -> Response:
        response.headers["x-response-id"] += "1"
        return response


class Second(BaseMiddleware):
    def process_request(self, request: Request) -> Request:
        request.headers["x-request-id"] += "2"
        return super().process_request(request)

    def process_response(self, response: Response) -> Response:
        response.headers["x-response-id"] = "2"
        return response


def test_chain_on_instance_access_without_default_middleware() -> None:
    response = factories.make_response(b"")
    driver1 = factories.DriverMock(response)
    driver2 = factories.DriverMock(response)
    assert driver1.middleware == []
    assert driver2.middleware == []
    assert driver1.middleware is not driver2.middleware


def test_chain_on_instance_access_with_default_middleware() -> None:
    chain = MiddlewareChain(First)
    with mock.patch.object(factories.DriverMock, "middleware", chain):
        response = factories.make_response(b"")
        driver1 = factories.DriverMock(response)
        driver2 = factories.DriverMock(response)
        assert driver1.middleware == [First]
        assert driver2.middleware == [First]
        assert driver1.middleware is not driver2.middleware


def test_chain_on_class_access() -> None:
    driver_cls = factories.DriverMock
    assert driver_cls.middleware == []
    assert driver_cls.middleware is driver_cls.middleware


def test_chain_returns_different_objects_on_instance_and_class_access() -> None:
    response = factories.make_response(b"")
    driver = factories.DriverMock(response)
    assert driver.middleware is not factories.DriverMock.middleware


def test_chain_on_instance_set_new_middleware() -> None:
    response = factories.make_response(b"")
    driver1 = factories.DriverMock(response)
    driver2 = factories.DriverMock(response)
    driver2.middleware = [First]
    assert factories.DriverMock.middleware == []
    assert driver1.middleware == []
    assert driver2.middleware == [First]


def test_chain_on_instance_set_new_middleware_with_defaults() -> None:
    chain = MiddlewareChain(First)
    with mock.patch.object(factories.DriverMock, "middleware", chain):
        response = factories.make_response(b"")
        driver = factories.make_driver(response)
        driver.middleware = [Second]
        assert driver.middleware == [First, Second]
        assert factories.DriverMock.middleware == [First]

        driver.middleware = [Second, First]
        assert driver.middleware == [Second, First]

        driver.middleware = []
        assert driver.middleware == [First]


def test_chain_order_of_execution_in_driver() -> None:
    response_mock = factories.make_response(b"")
    driver = factories.make_driver(response_mock, First, Second)
    response = driver.fetch(Request(Method.GET, "", ""))
    assert response.request.headers["x-request-id"] == "12"
    assert response.headers["x-response-id"] == "21"


@pytest.mark.asyncio
async def test_chain_order_of_execution_in_async_driver() -> None:
    response_mock = factories.make_response(b"")
    driver = factories.make_async_driver(response_mock, First, Second)
    response = await driver.fetch(Request(Method.GET, "", ""))
    assert response.request.headers["x-request-id"] == "12"
    assert response.headers["x-response-id"] == "21"
