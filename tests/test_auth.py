from apiwrappers.auth import ApiKeyAuth, BasicAuth, TokenAuth


def test_basic_auth_string_representation():
    auth = BasicAuth("username", "password")
    assert str(auth) == "Basic dXNlcm5hbWU6cGFzc3dvcmQ="


def test_basic_auth_representation():
    auth = BasicAuth("username", "password")
    assert repr(auth) == "<BasicAuth 'username'>"


def test_basic_auth():
    auth = BasicAuth("username", "password")
    assert auth() == {"Authorization": "Basic dXNlcm5hbWU6cGFzc3dvcmQ="}


def test_token_auth_string_representation():
    auth = TokenAuth("dXNlcm5hbWU6cGFzc3dvcmQ=")
    assert str(auth) == "Bearer dXNlcm5hbWU6cGFzc3dvcmQ="


def test_token_auth_representation():
    auth = TokenAuth("dXNlcm5hbWU6cGFzc3dvcmQ=")
    assert repr(auth) == "<TokenAuth 'Bearer ...'>"


def test_token_auth():
    auth = TokenAuth("dXNlcm5hbWU6cGFzc3dvcmQ=")
    assert auth() == {"Authorization": "Bearer dXNlcm5hbWU6cGFzc3dvcmQ="}


def test_apikey_auth_string_representation():
    auth = ApiKeyAuth(key="dXNlcm5hbWU6cGFzc3dvcmQ=", header="apikey")
    assert str(auth) == "apikey dXNlcm5hbWU6cGFzc3dvcmQ="


def test_apikey_auth_representation():
    auth = ApiKeyAuth(key="dXNlcm5hbWU6cGFzc3dvcmQ=", header="apikey")
    assert repr(auth) == "<ApiKeyAuth 'apikey ...'>"


def test_apikey_auth():
    auth = ApiKeyAuth(key="dXNlcm5hbWU6cGFzc3dvcmQ=", header="apikey")
    assert auth() == {"apikey": "dXNlcm5hbWU6cGFzc3dvcmQ="}
