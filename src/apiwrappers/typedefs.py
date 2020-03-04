from __future__ import annotations

from typing import Any, BinaryIO, Dict, Iterable, List, Mapping, Optional, Tuple, Union

ClientCert = Union[str, None, Tuple[str, str]]
Data = Union[str, None, Mapping[str, Any], Iterable[Tuple[str, Any]]]
FilesValue = Union[BinaryIO, Tuple[str, BinaryIO], Tuple[str, BinaryIO, str]]
Files = Optional[Dict[str, FilesValue]]
JSON = Union[str, int, float, bool, None, Mapping[str, Any], List[Any]]
QueryParams = Mapping[str, Optional[Iterable[str]]]
Timeout = Union[int, float, None]
Verify = Union[bool, str]
