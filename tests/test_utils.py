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


@pytest.mark.parametrize(
    ["data", "key", "expected"],
    [
        ({"id": 1}, None, {"id": 1}),
        ({"id": 1}, "id", 1),
        ({"item": {"id": 1}}, "item.id", 1),
        ({"items": [1, 2]}, "items.0", 1),
    ],
)
def test_getitem(data, key, expected):
    item = utils.getitem(data, key)
    assert item == expected


def test_getitem_raises_error():
    with pytest.raises(TypeError):
        utils.getitem("id", "id")
