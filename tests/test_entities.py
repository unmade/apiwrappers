import pytest

from apiwrappers import Method, Request

from . import factories


def test_compares_method_with_str():
    assert Method.GET == "get"
    assert Method.GET == "GET"
    assert Method.GET == Method("GET")


def test_method_string_representation():
    assert str(Method.GET) == "<Method [GET]>"


@pytest.mark.parametrize(
    ["data", "files", "json"],
    [
        (None, {"some": "files"}, {"some": "json"}),
        ({"some": "data"}, None, {"some": "json"}),
        ({"some": "data"}, {"some": "files"}, None),
    ],
)
def test_request_mutually_exclusive_parameters(data, files, json):
    with pytest.raises(ValueError) as excinfo:
        Request(
            Method.GET,
            "https://example.com",
            data=data,
            files=files,
            json=json,
        )
    expected = "`data`, `files` and `json` parameters are mutually exclusive"
    assert str(excinfo.value) == expected


def test_request_string_representation() -> None:
    request = Request(Method.GET, "https://example.com")
    assert str(request) == "<Request [GET]>"


def test_response_string_representation() -> None:
    response = factories.make_response(b"Hello, World!")
    assert str(response) == "<Response [200]>"
