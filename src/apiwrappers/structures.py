from typing import Dict, Iterator, Mapping, MutableMapping, Optional, Tuple, TypeVar

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
