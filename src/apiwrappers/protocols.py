import sys
from typing import Union

from apiwrappers.entities import AsyncResponse, Request, Response

if sys.version_info < (3, 8):
    from typing_extensions import Protocol
else:
    from typing import Protocol  # pylint: disable=no-name-in-module


class Driver(Protocol):
    timeout: Union[int, float, None]

    def fetch(self, request: Request) -> Response:
        ...


class AsyncDriver(Protocol):
    timeout: Union[int, float, None]

    async def fetch(self, request: Request) -> AsyncResponse:
        ...
