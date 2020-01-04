import pytest

from apiwrappers import Method, Request


def test_request_mutually_exclusive_parameters():
    with pytest.raises(ValueError):
        Request(
            Method.GET,
            host="https://example.com",
            path="/",
            data={"some": "data"},
            json={"some": "data"},
        )
