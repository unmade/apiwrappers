# pylint: disable=too-many-instance-attributes

import enum
from dataclasses import dataclass, field
from http.cookies import SimpleCookie
from typing import (
    Any,
    Awaitable,
    Callable,
    Iterable,
    List,
    Mapping,
    Optional,
    Tuple,
    Union,
)

from apiwrappers.structures import CaseInsensitiveDict

Data = Optional[Union[Mapping[str, Iterable[str]], Iterable[Tuple[str, str]]]]
JSON = Union[str, int, float, bool, None, Mapping[str, Any], List[Any]]
QueryParams = Mapping[str, Optional[Iterable[str]]]


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
    query_params: QueryParams = field(default_factory=dict)
    headers: Mapping[str, str] = field(default_factory=dict)
    cookies: Mapping[str, str] = field(default_factory=dict)
    data: Data = None
    json: Optional[JSON] = None
    verify_ssl: bool = True
    timeout: float = 1  # in seconds

    def __post_init__(self):
        if self.data is not None and self.json is not None:
            raise ValueError("`data` and `json` parameters are mutually exclusive")


@dataclass
class Response:
    status_code: int
    url: str
    headers: CaseInsensitiveDict[str]
    cookies: SimpleCookie
    content: bytes
    text: Callable[..., str]
    json: Callable[..., JSON]


@dataclass
class AsyncResponse:
    status_code: int
    url: str
    headers: CaseInsensitiveDict[str]
    cookies: SimpleCookie
    content: bytes
    text: Callable[..., Awaitable[str]]
    json: Callable[..., Awaitable[JSON]]
