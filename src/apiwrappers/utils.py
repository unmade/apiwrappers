import dataclasses
import os
import urllib.parse
from typing import Any, Mapping, Optional, TypeVar, Union, cast

from apiwrappers.typedefs import JSON

T = TypeVar("T")


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


def fromjson(obj: T, data: JSON) -> T:
    return cast(T, _fromjson(obj, data))


def _fromjson(obj, data):
    # pylint: disable=too-many-return-statements,too-many-branches
    if dataclasses.is_dataclass(obj):
        kwargs = {}
        for field in dataclasses.fields(obj):
            try:
                kwargs[field.name] = _fromjson(field.type, data[field.name])
            except KeyError:
                if field.default is not dataclasses.MISSING:
                    kwargs[field.name] = field.default
                elif field.default_factory is not dataclasses.MISSING:
                    kwargs[field.name] = field.default_factory()
                else:
                    raise
        return obj(**kwargs)
    if obj is Any:
        return data
    if hasattr(obj, "__origin__"):
        origin = obj.__origin__
        args = obj.__args__
        if origin in (list, set, tuple):
            if not isinstance(data, list):
                raise ValueError(f"Expected value to be list, got: {type(data)}")
            if origin is tuple and Ellipsis not in args:
                return origin(_fromjson(tp, item) for tp, item in zip(args, data))
            return origin(_fromjson(args[0], item) for item in data)
        if origin is dict:
            if not isinstance(data, Mapping):
                raise ValueError(f"Expected value to be mapping, got: {type(data)}")
            return origin(
                (_fromjson(args[0], k), _fromjson(args[1], v)) for k, v in data.items()
            )
        if origin is Union:
            if len(args) == 2 and isinstance(None, args[1]):
                if data is None:
                    return None
                return _fromjson(args[0], data)
            raise TypeError("Union is not supported")
        raise TypeError("Abstract types is not supported")
    return obj(data)
