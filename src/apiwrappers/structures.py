from typing import (
    Any,
    Dict,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    TypeVar,
)

from apiwrappers import utils

VT = TypeVar("VT")


class NoValue:
    __slots__: Tuple[str, ...] = tuple()

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class CaseInsensitiveDict(MutableMapping[str, VT]):
    __slots__ = ("_data",)

    def __init__(self, data: Optional[Mapping[str, VT]] = None, **kwargs: VT):
        self._data: Dict[str, Tuple[str, VT]] = {}
        if data is not None:
            self.update(data)
        self.update(kwargs)

    def __getitem__(self, key: str) -> VT:
        return self._data[key.lower()][1]

    def __setitem__(self, key: str, value: VT) -> None:
        self._data[key.lower()] = (key, value)

    def __delitem__(self, key: str) -> None:
        del self._data[key.lower()]

    def __iter__(self) -> Iterator[str]:
        return (original_key for original_key, value in self._data.values())

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        if self._data:
            return f"{self.__class__.__name__}({dict(self)})"
        return f"{self.__class__.__name__}()"


class Url:
    def __init__(self, url: str, **params: Any):
        self.template = url
        self.params = params

    def __str__(self) -> str:
        return self.template.format_map(self.params)

    def __repr__(self) -> str:
        params = ", ".join(f"{k}={repr(v)}" for k, v in self.params.items())
        if self.params:
            return f"{self.__class__.__name__}({repr(self.template)}, {params})"
        return f"{self.__class__.__name__}({repr(self.template)})"

    def __call__(self, path: str, **path_params: Any):
        url = utils.build_url(self.template, path)
        return Url(url, **{**self.params, **path_params})

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            return str(self) == other
        if isinstance(other, self.__class__):
            return self.template == other.template and self.params == other.params
        return NotImplemented
