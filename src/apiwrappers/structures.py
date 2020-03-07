from __future__ import annotations

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
    """
    Class to work with formatted string URLs and joining urls and path.

    Sometimes it useful to keep original format string in place, for example,
    for logging or metrics. This class stores original format string and its
    replacements fields, substituting it when needed.

    Args:
        template: a URL as format string, e.g. "https://example.org/users/{id}".
        replacements: values to format template with.

    Usage::

        >>> from apiwrappers import Url
        >>> url = Url("https://example.org")
        >>> url("/users/{id}", id=1)
        Url('https://example.org/users/{id}', id=1)
        >>> str(url("/users/{id}", id=1))
        'https://example.org/users/1'
    """

    def __init__(self, template: str, **replacements: Any):
        self.template = template
        self.replacements = replacements

    def __str__(self) -> str:
        return self.template.format_map(self.replacements)

    def __repr__(self) -> str:
        params = ", ".join(f"{k}={repr(v)}" for k, v in self.replacements.items())
        if self.replacements:
            return f"{self.__class__.__name__}({repr(self.template)}, {params})"
        return f"{self.__class__.__name__}({repr(self.template)})"

    def __call__(self, path: str, **replacements: Any) -> Url:
        """
        Joins path with current URL and return a new instance.

        Args:
            path: a path as format string, e.g. "/users/{id}".
            replacements: values to path with.

        Returns: New instance with a url joined with path.
        """
        url = utils.build_url(self.template, path)
        return Url(url, **{**self.replacements, **replacements})

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            return str(self) == other
        if isinstance(other, self.__class__):
            return (
                self.template == other.template
                and self.replacements == other.replacements
            )
        return NotImplemented
