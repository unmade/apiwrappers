# pylint: disable=too-many-instance-attributes

import enum
import json
from dataclasses import dataclass, field
from http.cookies import SimpleCookie
from typing import Mapping, cast

from apiwrappers.structures import CaseInsensitiveDict
from apiwrappers.typedefs import JSON, Data, QueryParams


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
    json: JSON = None

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
    encoding: str

    def text(self) -> str:
        return self.content.decode(self.encoding)

    def json(self) -> JSON:
        return cast(JSON, json.loads(self.content.decode(self.encoding)))
