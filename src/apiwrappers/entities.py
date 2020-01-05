# pylint: disable=too-many-instance-attributes

import enum
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Mapping, Optional, Union

JSON = Union[str, int, float, bool, None, Mapping[str, Any], List[Any]]

QueryParams = Mapping[str, Union[int, str, List[Union[int, str]]]]


class Method(enum.Enum):
    DELETE = "DELETE"
    HEAD = "HEAD"
    GET = "GET"
    PATCH = "PATCH"
    POST = "POST"
    PUT = "PUT"


@dataclass
class Request:
    method: Method
    host: str
    path: str
    data: Optional[Union[Dict[str, str], bytes]] = None
    json: Optional[Union[dict, List[dict]]] = None
    verify_ssl: bool = True
    timeout: float = 1  # in seconds

    def __post_init__(self):
        if self.data is not None and self.json is not None:
            raise ValueError("`data` and `json` parameters are mutually exclusive")


@dataclass
class Response:
    status_code: int
    url: str
    content: bytes
    text: Callable[..., str]
    json: Callable[..., JSON]


@dataclass
class AsyncResponse:
    status_code: int
    url: str
    content: bytes
    text: Callable[..., Awaitable[str]]
    json: Callable[..., Awaitable[JSON]]
