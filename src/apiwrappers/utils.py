import os
import urllib.parse
from typing import Mapping, Optional, Tuple

from apiwrappers.typedefs import JSON


class NoValue:
    __slots__: Tuple[str, ...] = tuple()


def build_url(host: str, path: str) -> str:
    scheme, netloc, prefix_path, query, fragment = urllib.parse.urlsplit(host)
    path = os.path.join(prefix_path, path.lstrip("/"))
    return urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))


def getitem(data: JSON, key: Optional[str]) -> JSON:
    if not key:
        return data
    parts = key.split(".")
    for part in parts:
        if isinstance(data, Mapping):
            data = data[part]
        elif isinstance(data, list):
            data = data[int(part)]
        else:
            raise TypeError(f"Expected `Mapping` or `List`, got: {type(data)}")
    return data
