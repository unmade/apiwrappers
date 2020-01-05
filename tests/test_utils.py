import pytest

from apiwrappers import utils


@pytest.mark.parametrize("host", ["http://example.com", "http://example.com/"])
@pytest.mark.parametrize(
    ["path", "expected"],
    [
        ("/join", "http://example.com/join"),
        ("join", "http://example.com/join"),
        ("join/", "http://example.com/join/"),
    ],
)
def test_build_url(host, path, expected):
    url = utils.build_url(host, path)
    assert expected == url
