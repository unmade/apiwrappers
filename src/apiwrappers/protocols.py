from typing import Union

from apiwrappers.compat import Protocol
from apiwrappers.entities import Request, Response
from apiwrappers.typedefs import Timeout
from apiwrappers.utils import NoValue


class Driver(Protocol):
    timeout: Timeout
    verify_ssl: bool

    def fetch(
        self,
        request: Request,
        timeout: Union[Timeout, NoValue] = NoValue(),
        verify_ssl: Union[bool, NoValue] = NoValue(),
    ) -> Response:
        ...


class AsyncDriver(Protocol):
    timeout: Timeout
    verify_ssl: bool

    async def fetch(
        self,
        request: Request,
        timeout: Union[Timeout, NoValue] = NoValue(),
        verify_ssl: Union[bool, NoValue] = NoValue(),
    ) -> Response:
        ...
