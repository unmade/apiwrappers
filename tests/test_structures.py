from apiwrappers import Url
from apiwrappers.structures import CaseInsensitiveDict, NoValue


def test_representation_no_value():
    assert repr(NoValue()) == "NoValue()"


def test_init_from_another_mapping():
    auth_token = "Basic YWxhZGRpbjpvcGVuc2VzYW1l"
    data = CaseInsensitiveDict(Authorization=auth_token)
    assert data["authorization"] == auth_token
    assert data["Authorization"] == auth_token


def test_init_with_named_arguments():
    auth_token = "Basic GVuc2VzYW1lYWxhZGRpbjpvc"
    data = CaseInsensitiveDict({"Authorization": auth_token})
    assert data["authorization"] == auth_token
    assert data["Authorization"] == auth_token


def test_del_item():
    auth_token = "Basic YWxhZGRpbjpvcGVuc2VzYW1l"
    data = CaseInsensitiveDict({"Authorization": auth_token})
    assert data.get("authorization") is auth_token
    del data["Authorization"]
    assert data.get("authorization") is None
    assert data.get("Authorization") is None


def test_len():
    data = CaseInsensitiveDict({"Content-Length": 1})
    assert len(data) == 1

    data = CaseInsensitiveDict({"Content-Length": 2, "Cache-Control": "no-cache"})
    assert len(data) == 2


def test_iter_returns_original_key():
    keys = ("Content-Length", "Cache-Control")
    values = (2, "no-cache")
    data = CaseInsensitiveDict(zip(keys, values))
    for i, key in enumerate(data):
        assert key == keys[i]


def test_repr():
    data = CaseInsensitiveDict({"Content-Length": 1})
    assert repr(data) == "CaseInsensitiveDict({'Content-Length': 1})"


def test_repr_with_empty_data():
    data = CaseInsensitiveDict()
    assert repr(data) == "CaseInsensitiveDict()"


def test_url_representation():
    url = Url("https://example.org")
    assert repr(url) == "Url('https://example.org')"

    url = Url("https://example.org/users/{id}", id=1)
    assert repr(url) == "Url('https://example.org/users/{id}', id=1)"


def test_url_string_representation():
    url = Url("https://example.org")
    assert url == "https://example.org"

    url = Url("https://example.org/users/{id}", id=1)
    assert url == "https://example.org/users/1"


def test_url_comparison():
    url_a = Url("https://example.org/users/{id}", id=1)
    url_b = Url("https://example.org/users/{id}", id=1)
    assert url_a == url_b

    url_a = Url("https://example.org/users/{id}", id=1)
    url_b = Url("https://example.org/users/{id}", id=2)
    assert url_a != url_b


def test_invalid_comparison():
    url = Url("https://example.org")
    assert url != 1


def test_url_join_path():
    url = Url("https://example.org")
    assert url("/users/{id}", id=1) == "https://example.org/users/1"

    url = Url("https://example.org")("/{version}", version="v1")("/users/{id}", id=1)
    assert url == "https://example.org/v1/users/1"
