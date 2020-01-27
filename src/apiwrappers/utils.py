import dataclasses
import os
import urllib.parse
from typing import (
    Any,
    Callable,
    Mapping,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
    get_type_hints,
)

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


def fromjson(objtype: Union[Callable[..., T], Type[T]], data: JSON) -> T:
    if objtype is Any:
        obj = data
    elif dataclasses.is_dataclass(objtype):
        obj = _handle_dataclass(objtype, data)
    elif _is_namedtuple(objtype):
        obj = _handle_namedtuple(objtype, data)
    elif _is_generic_type(objtype):
        obj = _handle_generic_type(objtype, data)
    else:
        obj = objtype(data)  # type: ignore
    return cast(T, obj)


def _is_namedtuple(obj: Any) -> bool:
    return hasattr(obj, "_fields") and issubclass(obj, tuple)


def _is_generic_type(obj: Any) -> bool:
    return hasattr(obj, "__origin__") and hasattr(obj, "__args__")


def _handle_dataclass(objtype: Any, data: JSON) -> Any:
    if not isinstance(data, Mapping):
        raise ValueError(f"Expected `Mapping`, got: {type(data)}")
    kwargs = {}
    hints = get_type_hints(objtype)
    for field in dataclasses.fields(objtype):
        try:
            kwargs[field.name] = fromjson(hints[field.name], data[field.name])
        except KeyError:
            if field.default is not dataclasses.MISSING:
                kwargs[field.name] = field.default
            # see: https://github.com/python/mypy/issues/6910
            elif field.default_factory is not dataclasses.MISSING:  # type: ignore
                kwargs[field.name] = field.default_factory()  # type: ignore
            else:
                raise
    return objtype(**kwargs)


def _handle_namedtuple(objtype: Any, data: JSON) -> Any:
    hints = get_type_hints(objtype)
    field_defaults = objtype._field_defaults  # pylint: disable=protected-access
    if isinstance(data, list):
        return objtype(*[fromjson(tp, item) for tp, item in zip(hints.values(), data)])
    if isinstance(data, Mapping):
        kwargs = {}
        for field_name, tp in hints.items():
            try:
                kwargs[field_name] = fromjson(tp, data[field_name])
            except KeyError:
                if field_name not in field_defaults:
                    raise
                kwargs[field_name] = field_defaults[field_name]
        return objtype(**kwargs)
    raise ValueError(f"Expected `List` or `Mapping`, got: {type(data)}")


def _handle_generic_type(objtype: Any, data: JSON) -> Any:
    origin = objtype.__origin__
    args = objtype.__args__
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
