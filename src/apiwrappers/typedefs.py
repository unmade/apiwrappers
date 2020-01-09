from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union

Data = Union[str, None, Mapping[str, Any], Iterable[Tuple[str, Any]]]
JSON = Union[str, int, float, bool, None, Mapping[str, Any], List[Any]]
QueryParams = Mapping[str, Optional[Iterable[str]]]
Timeout = Union[int, float, None]
