# pylint: disable=import-outside-toplevel

import pytest

from apiwrappers import make_driver


def test_make_driver_unexisting_driver() -> None:
    with pytest.raises(ValueError):
        make_driver("driver_does_not_exists")


@pytest.mark.requests
def test_make_driver_requests() -> None:
    from apiwrappers.drivers.requests import RequestsDriver

    driver = make_driver("requests")
    assert isinstance(driver, RequestsDriver)


@pytest.mark.aiohttp
def test_make_driver_aiohttp() -> None:
    from apiwrappers.drivers.aiohttp import AioHttpDriver

    driver = make_driver("aiohttp")
    assert isinstance(driver, AioHttpDriver)
