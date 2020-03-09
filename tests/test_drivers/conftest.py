# pylint: disable=import-outside-toplevel

import pytest


@pytest.fixture
def httpbin_ca_bundle():
    # original httpbin_ca_bundle fixture only sets REQUESTS_CA_BUNDLE env.
    # This is not suitable for other HTTP clients, so instead, we return
    # path to a valid CA bundle.
    from pytest_httpbin import certs

    return certs.where()
