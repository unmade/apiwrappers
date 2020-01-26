import dataclasses
import os
import urllib.parse
from typing import Any, Mapping, Optional, Type, TypeVar, Union, cast, get_type_hints

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
            raise TypeError(f"Expected `List` or `Mapping`, got: {type(data)}")
    return data


def fromjson(obj: Type[T], data: JSON) -> T:
    if obj is Any:
        return cast(T, data)
    if dataclasses.is_dataclass(obj):
        return cast(T, handle_dataclass(obj, data))
    if is_namedtuple(obj):
        return cast(T, handle_namedtuple(obj, data))
    if is_generic_type(obj):
        return cast(T, handle_generic_type(obj, data))
    return obj(data)  # type: ignore


def is_namedtuple(obj: Any) -> bool:
    return hasattr(obj, "_fields") and issubclass(obj, tuple)


def is_generic_type(obj: Any) -> bool:
    return hasattr(obj, "__origin__") and hasattr(obj, "__args__")


def handle_dataclass(obj, data):
    kwargs = {}
    hints = get_type_hints(obj)
    for field in dataclasses.fields(obj):
        try:
            kwargs[field.name] = fromjson(hints[field.name], data[field.name])
        except KeyError:
            if field.default is not dataclasses.MISSING:
                kwargs[field.name] = field.default
            elif field.default_factory is not dataclasses.MISSING:
                kwargs[field.name] = field.default_factory()
            else:
                raise
    return obj(**kwargs)


def handle_namedtuple(obj, data):
    field_types = obj._field_types  # pylint: disable=protected-access
    field_defaults = obj._field_defaults  # pylint: disable=protected-access
    if isinstance(data, list):
        return obj(
            *[fromjson(tp, item) for tp, item in zip(field_types.values(), data)]
        )
    if isinstance(data, Mapping):
        kwargs = {}
        for field_name, tp in field_types.items():
            try:
                kwargs[field_name] = fromjson(tp, data[field_name])
            except KeyError:
                if field_name not in field_defaults:
                    raise
                kwargs[field_name] = field_defaults[field_name]
        return obj(**kwargs)
    raise ValueError(f"Expected `List` or `Mapping`, got: {type(data)}")


def handle_generic_type(obj, data):
    origin = obj.__origin__
    args = obj.__args__
    if origin in (list, set, tuple):
        if not isinstance(data, list):
            raise ValueError(f"Expected `List`, got: {type(data)}")
        if origin is tuple and Ellipsis not in args:
            return origin(fromjson(tp, item) for tp, item in zip(args, data))
        return origin(fromjson(args[0], item) for item in data)
    if origin is dict:
        if not isinstance(data, Mapping):
            raise ValueError(f"Expected `Mapping`, got: {type(data)}")
        return origin(
            (fromjson(args[0], k), fromjson(args[1], v)) for k, v in data.items()
        )
    if origin is Union:
        if len(args) == 2 and isinstance(None, args[1]):
            if data is None:
                return None
            return fromjson(args[0], data)
        raise TypeError("Union is not supported")
    raise TypeError("Abstract types is not supported")
