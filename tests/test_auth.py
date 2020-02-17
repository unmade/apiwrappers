from apiwrappers.auth import BasicAuth


def test_basic_auth_string_representation():
    auth = BasicAuth("username", "password")
    assert str(auth) == "Basic dXNlcm5hbWU6cGFzc3dvcmQ="


def test_basic_auth_representation():
    auth = BasicAuth("username", "password")
    assert repr(auth) == "<BasicAuth 'username'>"


def test_basic_auth():
    auth = BasicAuth("username", "password")
    assert auth() == {"Authorization": "Basic dXNlcm5hbWU6cGFzc3dvcmQ="}
