from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Mapping,
    Optional,
    Tuple,
    Union,
)

if TYPE_CHECKING:
    # pylint: disable=cyclic-import
    from apiwrappers.entities import Request, Response  # noqa: F401

SimpleAuth = Callable[[], Dict[str, str]]
AuthFlow = Callable[[], Generator["Request", "Response", Dict[str, str]]]
Auth = Optional[Union[Tuple[str, str], SimpleAuth, AuthFlow]]

ClientCert = Union[str, None, Tuple[str, str]]
Data = Union[str, None, Mapping[str, Any], Iterable[Tuple[str, Any]]]
FilesValue = Union[BinaryIO, Tuple[str, BinaryIO], Tuple[str, BinaryIO, str]]
Files = Optional[Dict[str, FilesValue]]
Json = Union[str, int, float, bool, None, Mapping[str, Any], List[Any]]
QueryParams = Mapping[str, Optional[Iterable[str]]]
Timeout = Union[int, float, None]
Verify = Union[bool, str]
