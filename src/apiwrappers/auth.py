import base64
from typing import Dict


class BasicAuth:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def __str__(self) -> str:
        credentials = f"{self.username}:{self.password}".encode()
        return f"Basic {base64.b64encode(credentials).strip().decode()}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.username}'>"

    def __call__(self) -> Dict[str, str]:
        return {"Authorization": str(self)}


class TokenAuth:
    def __init__(self, token: str, kind: str = "Bearer"):
        self.token = token
        self.kind = kind

    def __str__(self) -> str:
        return f"{self.kind} {self.token}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.kind} ...'>"

    def __call__(self) -> Dict[str, str]:
        return {"Authorization": str(self)}


class ApiKeyAuth:
    def __init__(self, key: str, header: str = "X-Api-Key"):
        self.key = key
        self.header = header

    def __str__(self) -> str:
        return f"{self.header}:{self.key}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.header} ...'>"

    def __call__(self) -> Dict[str, str]:
        return {self.header: self.key}
