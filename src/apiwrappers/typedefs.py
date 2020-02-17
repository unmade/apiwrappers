from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple, Union

Data = Union[str, None, Mapping[str, Any], Iterable[Tuple[str, Any]]]
JSON = Union[str, int, float, bool, None, Mapping[str, Any], List[Any]]
QueryParams = Mapping[str, Optional[Iterable[str]]]
Timeout = Union[int, float, None]

SimpleAuth = Callable[[], Dict[str, str]]
Auth = Optional[Union[Tuple[str, str], SimpleAuth]]
